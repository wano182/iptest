import argparse

import re

import subprocess
import threading

def extract_ips(file):
    with open(file, "r") as file:
        # 读取文件内容
        file_contents = file.read()

    # 使用正则表达式提取IP地址
    ips = re.findall(r'\d+\.\d+\.\d+\.\d+', file_contents)

    return ips

# 定义ping操作的函数
def ping(ips):
    result_ips=[]

    def ping(ip):
        try:
            # 构建ping命令
            ping_cmd = f"ping -n 4 {ip}"  # 在Linux/macOS上使用-c 4，在Windows上使用-n 4
        
            # 执行ping命令
            result = subprocess.run(ping_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
            # 提取并存储目标行
            lines = result.stdout.splitlines()
            target_line = lines[-1]

            # 将ping结果添加到列表中
            result_ips.append(f"{ip,target_line}")
        
        except Exception as e:
            result_ips.append(f"无法ping通IP地址 {ip}，错误信息：{str(e)}")

    # 创建线程来执行ping操作
    threads = []
    for ip in ips:
        thread = threading.Thread(target=ping, args=(ip,))
        threads.append(thread)
        thread.start()

    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    return result_ips

# 提取可连接ip
def pure(results):
    pure_result=[]
    for result in results:
        if '100% loss' not in result:
            pure_result.append(result)
    return pure_result

def compare_average(item):
    # 使用正则表达式提取Average的值
    import re
    match = re.search(r'Average = (\d+)ms', item)
    if match:
        return int(match.group(1))
    return 0

def silit(datas):
    # 初始化一个空列表，用于存储简化后的信息
    simplified_data = []

    # 循环遍历每一行，并提取所需信息
    for line in datas:
        parts = line.strip('()').split(', ')
        ip_address = parts[0].strip("'")
        minimum = parts[1].split('=')[1].strip()
        maximum = parts[2].split('=')[1].strip()
        average = parts[3].split('=')[1].strip().strip("')")
    
        # 格式化成简洁的字符串并添加到列表中
        simplified_data.append(f'IP: {ip_address}\tminimum: {minimum}\tmaximum: {maximum}\taverage: {average}')

    return simplified_data

def main(args):
    for file in args.i:

        # 提取ip
        ips=extract_ips(file)

        # 进行ping
        results=ping(ips)

        # 按照Average的值从大到小排序
        rank_pure_ips = sorted(pure(results), key=compare_average, reverse=False)

        # 美化结果
        end_data = silit(rank_pure_ips)

        # 输出排序结果
        output_filename="result_" + file
        with open(output_filename,"w") as f:
            f.write("\n".join(end_data))

    return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-i', type=str, nargs="*",
                        help='Input files')
    args = parser.parse_args()
    main(args)
    