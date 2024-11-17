def sort_data_by_checkin_time(user_data, sampled_dataset):
    for i in range(len(sampling_rates)):
        for user_id in user_data[i]:
            user_data[i][user_id] = sorted(user_data[i][user_id], key=lambda x: x[0])
        sampled_dataset[i] = sorted(sampled_dataset[i], key=lambda x: x[1])

# Call this function after the sampling process
sort_data_by_checkin_time(user_data, sampled_dataset)



# Write the sorted sampled data to the output file
# Output files to store sampled data
output_files = ['sampled_output_0.2.txt', 'sampled_output_0.1.txt', 'sampled_output_0.05.txt', 'sampled_output_0.025.txt']

for i in range(len(sampling_rates)):
    with open(output_files[i], 'w') as output:
        for data in sampled_dataset[i]:
            output_line = '\t'.join([str(data[0]), str(data[1]), str(data[2]), str(data[3]), str(data[4])]) + '\n'
            output.write(output_line)
    print("Writing to file completed:", output_files[i])
    
foutput_files = ['f_0.2.txt', 'f_0.1.txt', 'f_0.05.txt', 'f_0.025.txt']
# Write the sampled data to the output file
for i in range(len(sampling_rates)):
    with open(foutput_files[i], 'w') as output:
        for user_id, data in user_data[i].items():
            for checkin in data:
                output_line = '\t'.join([str(user_id), str(checkin[0]), str(checkin[1]), str(checkin[2]), str(checkin[3])]) + '\n'
                output.write(output_line)
    print("Writing to file completed:", foutput_files[i])




def find_checkin_time(user_data, user_id, target_checkin_time):
    if user_id in user_data:
        user_checkins = user_data[user_id]
        checkin_times = [checkin_data[0] for checkin_data in user_checkins]  # Assuming checkin_time is the first element
        if target_checkin_time in checkin_times:
            index = checkin_times.index(target_checkin_time)
            if index < len(user_checkins) - 1:
                return user_checkins[index + 1][0]
    return None



def build_contact_network_optimized(sampled_data, sampling_rate_index, d_max=D_MAX, time_window=TIME_WINDOW):
    # 创建主接触网络
    contact_network = defaultdict(list)
    user_location_time_dict = {}  # 临时字典储存用户位置和timestamp
    user_contacting_with_dict = {} # 正在接触的位置
    # 遍历数据集
    for i in range(len(sampled_data)):
        user_id_i, timestamp_i, lat_i, lon_i, _ = sampled_data[i]
        
        # 检查临时字典中是否存在当前用户id，如果不存在则添加
        if user_id_i not in user_location_time_dict:
            user_location_time_dict[user_id_i] = (user_id_i, lat_i, lon_i, timestamp_i)
        else:
            # 更新位置和timestamp信息
            user_location_time_dict[user_id_i] = (user_id_i, lat_i, lon_i, timestamp_i)
       
        # 历变临时字典网络寻找相邻的点并记录
        for user_id_j, (user_id_j, lat_j, lon_j, timestamp_j) in user_location_time_dict.items():
            if user_id_i == user_id_j:
                continue  # 跳过自身
            
            set_key = frozenset({user_id_i, user_id_j})
            # 计算距离
            distance = geodesic((lat_i, lon_i), (lat_j, lon_j)).meters

            
            # 少于限制距离就记录到临时接触网络
            if distance < d_max:
                # 寻找分开时的timestamp
                # 没有下一个timestamp就将终点设置为最大日期限制
                end_time_i = find_checkin_time(user_data[sampling_rate_index], user_id_i, timestamp_i) or end_date
                end_time_j = find_checkin_time(user_data[sampling_rate_index], user_id_j, timestamp_j) or end_date
                end_time = min(end_time_i, end_time_j)
                
                # 查询是否连续接触
                if set_key in user_contacting_with_dict:
                    # 更新结束timestamp
                    user_contacting_with_dict[set_key][1] = end_time
                else:
                    # 记录接触信息
                    user_contacting_with_dict[set_key] = [timestamp_j, end_time]
                    
            # 大于距离就储存到全局接触网络
            elif set_key in user_contacting_with_dict:
                start_timestamp = user_contacting_with_dict[set_key][0]
                end_timestamp = user_contacting_with_dict[set_key][1]
                duration = (end_timestamp - start_timestamp).total_seconds()
                contact_network[user_id_i].append((user_id_j, start_timestamp, end_timestamp, duration))
                contact_network[user_id_j].append((user_id_i, start_timestamp, end_timestamp, duration))
                print(f"User {user_id_i} had contact with User {user_id_j} from {start_timestamp} to {end_timestamp}, duration: {duration} seconds")
                # 清除接触信息
                del user_contacting_with_dict[set_key]

    # 结束历变后再检查一次还有没有临时网络没被添加
    for key, value in user_contacting_with_dict.items():
        user_ids = list(key)
        user_id_i = user_ids[0]
        user_id_j = user_ids[1]
        start_timestamp = value[0]
        end_timestamp = value[1]
        duration = (end_timestamp - start_timestamp).total_seconds()
        contact_network[user_id_i].append((user_id_j, start_timestamp, end_timestamp, duration))
        contact_network[user_id_j].append((user_id_i, start_timestamp, end_timestamp, duration))
        print(f"User {user_id_i} had contact with User {user_id_j} from {start_timestamp} to {end_timestamp}, duration: {duration} seconds")
            
    return contact_network

# 调用函数生成接触网络
contact_graph = build_contact_network_optimized(sampled_dataset[3], 3)
print("Contact Graph Generated Successfully!")
    
