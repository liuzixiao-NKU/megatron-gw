import sys
sys.path.append('/workspace/zhouy/megatron-gw/GWToolkit/')
from gwtoolkit.gw.ray import RayDatasetTorch, RayDataset, ray
import msgpack_numpy as m
m.patch()               # Important line to monkey-patch for numpy support!

import redis
import numpy as np
from tqdm import tqdm

connection_pool = redis.ConnectionPool(host='localhost', port=5153, db=0, decode_responses=False)
r = redis.Redis(connection_pool=connection_pool)

def toRedis(value,name):
    """Store given Numpy array 'value' in Redis under key 'name'"""
    r.set(name,m.packb(value))
    return

from torch.utils.data import DataLoader
# import ray

import numpy as np


def update_level(i):
    if i%100==0:
        return 4
    elif i%50==0:
        return 3
    elif i%10==0:
        return 2
    else:
        return 1
    # np.array([update_level(i) for i in range(1000)])


batch_size = 1
num_dataset = 32 if batch_size >= 32 else batch_size
num_range = batch_size//num_dataset
num_repeat = 4


datasets = RayDatasetTorch.remote(num_dataset=num_dataset)

start = 0
end = 1_000

for index in tqdm(range(start//num_repeat, end//num_repeat)):

        level = update_level(index)
        pipeline = datasets.pipeline.remote(num_range, num_repeat, batch_size, level=level)
        iteration = iter(ray.get(pipeline))
        for i, _ in enumerate(range(num_repeat)):
            # if is_exist_Redis(f'data_{index}_{i}'):
            seed = np.random.rand()

            (data, signal, params) = next(iteration)
            toRedis(data, f'data_{index}_{i}')
            toRedis(seed, f'seed_data_{index}_{i}')

            toRedis(signal, f'signal_{index}_{i}')
            toRedis(seed, f'seed_signal_{index}_{i}')

            toRedis(params, f'params_{index}_{i}')
            toRedis(seed, f'seed_params_{index}_{i}')

ray.shutdown()
