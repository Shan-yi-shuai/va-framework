import os
import json
import pandas as pd
import json
from datetime import datetime, timedelta
from collections import Counter
from collections import defaultdict
import numpy as np
from sklearn.manifold import TSNE
from tslearn.metrics import cdist_dtw
from tslearn.preprocessing import TimeSeriesScalerMeanVariance

PATH_DATA_FOLDER = './data/'
FILE_DATA_JSON = 'data.json'

ENTITY_TYPES = {
    'document': {'delivery_report': 'Entity.Document.DeliveryReport'},
    'vessel': {'fishing_vessel': 'Entity.Vessel.FishingVessel',
               'cargo_vessel': 'Entity.Vessel.CargoVessel',
               'tour_vessel': 'Entity.Vessel.Tour',
               'other_vessel': 'Entity.Vessel.Other',
               'research_vessel': 'Entity.Vessel.Research',
               'ferry_vessel': {'passenger_vessel': 'Entity.Vessel.Ferry.Passenger',
                                 'cargo_vessel': 'Entity.Vessel.Ferry.Cargo'}
               },
    'location': {'point': 'Entity.Location.Point',
                 'city': 'Entity.Location.City',
                 'region': 'Entity.Location.Region',
                 },
    'commodity': {'fish': 'Entity.Commodity.Fish'}
}

EVENT_TYPES = {
    'transport_event': 'Event.TransportEvent.TransponderPing',
    'transaction': 'Event.Transaction',
    'harbor_report': 'Event.HarborReport',
}


class Model:
    def __init__(self):
        self.DATA_FOLDER = PATH_DATA_FOLDER

        try:
            with open(os.path.join(self.DATA_FOLDER, FILE_DATA_JSON), 'r') as file:
                mc2 = json.load(file)
                self.entities = mc2['nodes']
                self.events = mc2['links']
        except Exception as e:
            print(f'could not open: {FILE_DATA_JSON} because {e}')

        self.date_movements = self.get_date_movements()
        self.filtered_movements = []

    def get_events(self, event_type):
        return pd.DataFrame([event for event in self.events if event['type'] == event_type])

    def get_entities(self, entity_type):
        return pd.DataFrame([entity for entity in self.entities if entity['type'] == entity_type])

    def get_entities_vague(self, entity_type):
        return pd.DataFrame([entity for entity in self.entities if entity['type'].startswith(entity_type)])

    def get_entity(self, entity_id):
        return pd.DataFrame([entity for entity in self.entities if entity['id'] == entity_id])

    def get_date_movements(self):
        self.date_movements = []
        df_transport_events = pd.DataFrame(
            self.get_events(EVENT_TYPES['transport_event']))

        if not df_transport_events.empty:
            # 尝试第一种格式解析日期时间
            df_transport_events['start_time'] = pd.to_datetime(
                df_transport_events['time'], errors='coerce', format="%Y-%m-%dT%H:%M:%S.%f")
            # 对于解析失败的，使用第二种格式
            mask = df_transport_events['start_time'].isna()
            df_transport_events.loc[mask, 'start_time'] = pd.to_datetime(
                df_transport_events.loc[mask, 'time'], format="%Y-%m-%dT%H:%M:%S")

            df_transport_events['end_time'] = df_transport_events['start_time'] + \
                pd.to_timedelta(df_transport_events['dwell'], unit='s')

            # 将数据按天拆分
            for _, row in df_transport_events.iterrows():
                location_id = row['source']
                vessel_id = row['target']
                start_time = row['start_time']
                end_time = row['end_time']

                current_date = start_time
                while current_date.date() <= end_time.date():
                    if current_date.date() == start_time.date():
                        if current_date.date() == end_time.date():
                            dwell = (end_time - start_time).total_seconds()
                        else:
                            dwell = (datetime.combine(
                                current_date.date(), datetime.max.time()) - start_time).total_seconds()
                    elif current_date.date() == end_time.date():
                        dwell = (end_time - datetime.combine(current_date.date(),
                                 datetime.min.time())).total_seconds()
                    else:
                        dwell = 24 * 3600  # Full day in seconds

                    self.date_movements.append({
                        'date': current_date.strftime("%Y-%m-%d"),
                        'location_id': location_id,
                        'vessel_id': vessel_id,
                        'type': 'transport',
                        'dwell': dwell
                    })
                    current_date += timedelta(days=1)

        return self.date_movements

    def get_vessel_time_series(self, start_date, end_date, vessel_ids, location_ids):
        location_indices = {location: index for index,
                            location in enumerate(location_ids)}
        # 生成日期列表
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        date_list = [(start + timedelta(days=x)).strftime("%Y-%m-%d")
                     for x in range((end - start).days + 1)]
        filtered_movements = [record for record in self.date_movements if record['vessel_id'] in vessel_ids and record['date'] in date_list and record['location_id']
                              in location_ids and datetime.strptime(record['date'], "%Y-%m-%d") >= start and datetime.strptime(record['date'], "%Y-%m-%d") <= end]
        result_count = defaultdict(
            lambda: defaultdict(lambda: [0] * len(location_ids)))
        result_dwell = defaultdict(
            lambda: defaultdict(lambda: [0] * len(location_ids)))

        for record in filtered_movements:
            vessel_id = record['vessel_id']
            date = record['date']
            location_id = record['location_id']
            dwell = record['dwell']

            # 增加对应位置的停留时间
            result_dwell[vessel_id][date][location_indices[location_id]] += dwell

            # 增加对应位置的计数
            result_count[vessel_id][date][location_indices[location_id]] += 1

        final_result = {}
        for vessel in result_count.keys():
            final_result[vessel] = []
            for date in date_list:
                counts = result_count[vessel][date]
                dwells = result_dwell[vessel][date]
                combined = [(count, dwell)
                            for count, dwell in zip(counts, dwells)]
                final_result[vessel].append([date, combined])

        return final_result

    def get_vessel_tsne(self, final_result):
        # 提取时间序列数据
        time_series_data = []
        vessels = []

        for vessel, data in final_result.items():
            time_series = [entry[1] for entry in data]
            time_series_data.append(time_series)
            vessels.append(vessel)
        # 转换为 numpy 数组并标准化
        time_series_data = np.array(time_series_data)
        # 展开二维数据并进行标准化
        n_samples, n_timesteps, n_locations, n_features = time_series_data.shape
        time_series_data = time_series_data.reshape(
            n_samples, n_timesteps, n_locations * n_features)
        time_series_data = TimeSeriesScalerMeanVariance().fit_transform(time_series_data)

        # 计算时间序列之间的 TW 距离矩阵
        dtw_distances = cdist_dtw(time_series_data)
        tsne = TSNE(n_components=2, perplexity=50, random_state=0)
        transformed_data = tsne.fit_transform(dtw_distances)
        transformed_data = transformed_data.astype(float).tolist()
        return json.dumps([[vessel, coord] for vessel, coord in zip(vessels, transformed_data)])

    def get_all_entities(self):
        return json.dumps(self.entities)

    def get_vessel_movements(self, start_date, end_date, location_ids):
        df_transport_events = pd.DataFrame(
            self.get_events(EVENT_TYPES['transport_event'])
        )

        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        if not df_transport_events.empty:
            # 尝试第一种格式解析日期时间
            df_transport_events['start_time'] = pd.to_datetime(
                df_transport_events['time'], errors='coerce', format="%Y-%m-%dT%H:%M:%S.%f"
            )
            # 对于解析失败的，使用第二种格式
            mask = df_transport_events['start_time'].isna()
            df_transport_events.loc[mask, 'start_time'] = pd.to_datetime(
                df_transport_events.loc[mask,
                                        'time'], format="%Y-%m-%dT%H:%M:%S"
            )

            df_transport_events['end_time'] = df_transport_events['start_time'] + \
                pd.to_timedelta(df_transport_events['dwell'], unit='s')

            # 修改 start_time 和 end_time
            df_transport_events['start_time'] = df_transport_events['start_time'].apply(
                lambda x: max(x, start))
            df_transport_events['end_time'] = df_transport_events['end_time'].apply(
                lambda x: min(x, end))

            df_transport_events_rename = df_transport_events.rename(
                columns={'source': 'location_id', 'target': 'vessel_id'})

            filtered_movements = df_transport_events_rename[
                (df_transport_events_rename['location_id'].isin(location_ids)) &
                (df_transport_events_rename['end_time'] > start) &
                (df_transport_events_rename['start_time'] < end)
            ]
            filtered_movements = filtered_movements.assign(
                start_time=filtered_movements['start_time'].dt.strftime(
                    '%Y-%m-%dT%H:%M:%S'),
                end_time=filtered_movements['end_time'].dt.strftime(
                    '%Y-%m-%dT%H:%M:%S')
            )
            self.filtered_movements = filtered_movements[[
                'start_time', 'end_time', 'location_id', 'vessel_id']].to_dict(orient='records')

        return json.dumps(self.filtered_movements)

    def get_aggregated_vessel_movements(self, vessel_ids):
        df = pd.DataFrame(self.filtered_movements)
        df = df.loc[df['vessel_id'].isin(vessel_ids)]
        # 转换时间列为datetime格式
        df['start_time'] = pd.to_datetime(df['start_time'])
        df['end_time'] = pd.to_datetime(df['end_time'])

        # 获取所有时间点
        time_points = pd.concat([df['start_time'], df['end_time']]).drop_duplicates(
        ).sort_values().reset_index(drop=True)
        aggregated_results = []

        for i in range(len(time_points) - 1):
            start_interval = time_points[i]
            end_interval = time_points[i + 1]

            # 过滤在当前时间区间内的记录
            mask = (df['start_time'] < end_interval) & (
                df['end_time'] > start_interval)
            current_interval = df[mask]

            # 计算位置出现次数
            location_count = current_interval['location_id'].value_counts()

            if not location_count.empty:
                max_location = location_count.idxmax()
            else:
                max_location = None

            # 合并连续相同的location_id
            if aggregated_results and aggregated_results[-1]['location_id'] == max_location:
                aggregated_results[-1]['end_time'] = end_interval.isoformat()
            else:
                aggregated_results.append({
                    'start_time': start_interval.isoformat(),
                    'end_time': end_interval.isoformat(),
                    'location_id': max_location,
                    'vessel_id': 'aggregation'
                })

        return aggregated_results
