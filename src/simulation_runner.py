# File: simulation_runner.py

import random
from server_instance import ServerInstance
from apigateway import APIGateway

def generate_workload(case_type, num_requests=1000, num_items=250):
    """
    Membuat workload berdasarkan skenario kasus yang berbeda.
    """
    workload = []
    
    if case_type == 'Fokus Item Panas (80/20)':
        # Kasus standar: 80% request ke 20% item.
        num_hot_items = int(num_items * 0.2)
        hot_items = [f"item_{i}" for i in range(num_hot_items)]
        cold_items = [f"item_{i}" for i in range(num_hot_items, num_items)]
        for _ in range(num_requests):
            key = random.choice(hot_items) if random.random() < 0.8 else random.choice(cold_items)
            location = random.randint(1, 100)
            workload.append({'key': key, 'location': location})

    elif case_type == 'Fokus Lokasi':
        # 80% request datang dari satu rentang lokasi yang sempit.
        for _ in range(num_requests):
            key = f"item_{random.randint(0, num_items-1)}"
            location = random.randint(40, 60) if random.random() < 0.8 else random.randint(1, 100)
            workload.append({'key': key, 'location': location})
            
    elif case_type == 'Terdistribusi Merata':
        # Request tersebar merata, baik item maupun lokasi.
        for _ in range(num_requests):
            key = f"item_{random.randint(0, num_items-1)}"
            location = random.randint(1, 100)
            workload.append({'key': key, 'location': location})
            
    return workload

def run_experiment(lb_strategy, cache_policy, workload_case, num_servers=3, cache_size=10, num_requests=1000):
    """
    Menjalankan satu skenario simulasi lengkap dan mengembalikan hasilnya.
    """
    servers = [ServerInstance(f"S{i+1}", cache_policy, location=i*(100/3)+(100/6), cache_size=cache_size) for i in range(num_servers)]
    gateway = APIGateway(servers)
    workload = generate_workload(workload_case, num_requests=num_requests)
    request_per_server = [0] * num_servers
    max_active_conn = []

    cache_hits = 0
    total_response_time = 0

    for i, req in enumerate(workload):
        if i % 100 == 0:
            max_active_conn.append(max([s.active_connections for s in servers]))
        server = gateway.dispatch(lb_strategy, req['key'], req['location'])
        request_per_server[int(server.name[1:]) - 1] += 1
        is_hit, response_time = server.handle_request(req['key'], req['location'])
        if is_hit:
            cache_hits += 1
        total_response_time += response_time
    
    total_requests = len(workload)
    hit_ratio = (cache_hits / total_requests) * 100
    avg_resp_time = (total_response_time / total_requests) * 1000
    
    # Menambahkan workload_case ke hasil
    return {
        "Workload Case": workload_case,
        "LB Strategy": lb_strategy,
        "Cache Policy": cache_policy,
        "Avg Resp Time (ms)": avg_resp_time,
        "Cache Hit Ratio (%)": hit_ratio,
        "Requests per Server": request_per_server,
        "Max Active Connection": max_active_conn
    }
