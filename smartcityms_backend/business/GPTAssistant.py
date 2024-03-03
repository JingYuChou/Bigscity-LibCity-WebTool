import openai, json

from backend.settings import API_KEY, CONFIG_PATH

'''
这个脚本主要用于LibCity的后端ai助手
该助手主要有以下两个功能：
1. 回答关于LibCity的一些基本问题
2. 接受用户提供的参数（比如：数据集，任务，模型等）进行自动化创建实验

第一个功能主要靠对openai提供的GPT-3.5-fine-tuneing接口进行微调后实现
第二个功能主要包括下面几个步骤：
1. 读取参数存在某个json里面，我们认为是存在Mysql数据库中，和一个实验共存
2. 将目前所存储的所有参数进行检查，格式正确的时候调用接口创建实验并且执行
3. 关于json的刷新问题，我们认为是在其更新一个实验名称的时候进行刷新

关于创建实验，我的思路是这样的，首先需要user给几个决定性的参数，
比如任务，数据集，模型，实验名称等等可以使用一个特定的方法自动化生成
所以我们的std_json只需要有跑模型的参数就可以了，其他的参数都是可以自动化生成的，可见度什么的默认为不可见

#TODO:自动化生成实验的方法
#TODO:链接前端
'''

std_json = {
    "task_name": "",
    "task_name_show": "",
    "task_description": "",
    "creator": "",
    "execute_time": "",
    "execute_end_time": "",
    "task_status": "",
    "execute_msg": "",
    "visibility": "",
    "task": "",
    "model": "",
    "dataset": "",
    "config_file": "",
    "saved_model": "",
    "train": "",
    "batch_size": "",
    "train_rate": "",
    "eval_rate": "",
    "learning_rate": "",
    "max_epoch": "",
    "gpu": "",
    "gpu_id": "",
    "exp_id": "",
    "log_file_name": ""
}

file_links = {
    "TAXIBJ": "https://drive.google.com/file/d/1Ar-RixC_E4NaPNNP_ZUvKpIQePsBJ7zQ/view?usp=drive_link",
    "T_DRIVE20150206": "https://drive.google.com/file/d/1ZSUgMmkQGsBOIXkyR4665SsdMfRKvmcm/view?usp=drive_link",
    "T_DRIVE_SMALL": "https://drive.google.com/file/d/1JsclPvykCB3yUHTuUk3bCvIeojMTaJ5y/view?usp=drive_link",
    "SZ_TAXI": "https://drive.google.com/file/d/15JtkPjDx5KfvpZjUPA9PDu6EMeN_g7Fr/view?usp=drive_link",
    "SHMETRO": "https://drive.google.com/file/d/1sDHWx4Xi-nfnb5IRcRH2pKXIP0nVF-An/view?usp=drive_link",
    "serm_glove_word_vec": "https://drive.google.com/file/d/1hqi-WAqHHTsyoHRQ9WW-ynigYBfWYI2y/view?usp=drive_link",
    "Seattle": "https://drive.google.com/file/d/1MOyzSsw1qEyJhMzbTjWlPyvhs8SyoWRM/view?usp=drive_link",
    "ROTTERDAM": "https://drive.google.com/file/d/17aNUruX3rHwxr12RiT5LimajCVFt0Fp8/view?usp=drive_link",
    "Q-TRAFFIC": "https://drive.google.com/file/d/1t1DW82s1mw2yO76esvkiY0tA6H5aQZwv/view?usp=drive_link",
    "PORTO201307-201309": "https://drive.google.com/file/d/1dhMCLEB4B3ckGoqkjAmT9VfhC0lqQ-zj/view?usp=drive_link",
    "PEMSD8": "https://drive.google.com/file/d/1IYBfRTnhyrrpGofJNUzUDs6nc_I41SK-/view?usp=drive_link",
    "PEMSD7(M)": "https://drive.google.com/file/d/1i425AKg5DG807ldOaNzqKnBdChKC9zab/view?usp=drive_link",
    "PEMSD7": "https://drive.google.com/file/d/1GAmp0c0sOFuz8uIXp6Eu01soVjwhHvcz/view?usp=drive_link",
    "PEMSD4": "https://drive.google.com/file/d/1NuHSa1yY6ZPRsDdIv98zqmWDzAio3RAj/view?usp=drive_link",
    "PEMSD3": "https://drive.google.com/file/d/17zzexWxZTkfIoVM07RYoIZhFoM5qVgPJ/view?usp=drive_link",
    "PEMS_BAY": "https://drive.google.com/file/d/1M1MFTp58aiK8KHVkVjadgirbFO5A4Ht0/view?usp=drive_link",
    "NYCTaxi20160102": "https://drive.google.com/file/d/18QMWkrEdf2P-mkVe_clYrQecPWGbjS2J/view?usp=drive_link",
    "NYCTaxi20160103": "https://drive.google.com/file/d/1m_1uG5l6NIe3a_wNUwOC5eFd0_EtP8AM/view?usp=drive_link",
    "NYCTaxi20140112": "https://drive.google.com/file/d/1L9jNQbU5lDIpXHgk0evGlYeNOsKGzn5k/view?usp=drive_link",
    "NYCTAXI202004-202006_OD": "https://drive.google.com/file/d/1GdmfiakSgvh9TdzhtCPbCRDJIWtwsWIC/view?usp=drive_link",
    "NYCTAXI202001-202003_DYNA": "https://drive.google.com/file/d/10jMJ5RPDMEGi1qFw26IDem9dKKMo1g6n/view?usp=drive_link",
    "NYCTAXI201401-201403_GRID": "https://drive.google.com/file/d/1eDHTOIRCyQ6NARNpIB8SvquG5JpOkj8z/view?usp=drive_link",
    "NYCBike20160809": "https://drive.google.com/file/d/1aQ7-rsjlUIZgy3x6AhqWqX6R-Wl01RyL/view?usp=drive_link",
    "NYCBike20160708": "https://drive.google.com/file/d/1gTa0e8KHu-5ysCIgUK4zU_-gpJmcDxK2/view?usp=drive_link",
    "NYCBike20140409": "https://drive.google.com/file/d/1GRf5NyurxRG7a5RDjHliNvkFIS8nB7Lb/view?usp=drive_link",
    "NYCBike202007-202009": "https://drive.google.com/file/d/1Qz5xDm0cDjhWgbObj7mPI3UbB7wjf-eT/view?usp=drive_link",
    "NYC_TOD": "https://drive.google.com/file/d/1b_xTXGS-j-Cm6Ki8QfDxAdhznkH9Qq0p/view?usp=drive_link",
    "NYC_RISK": "https://drive.google.com/file/d/13E2oTSUs7JjFLt7bVHzR3rWJzmVSGKIZ/view?usp=drive_link",
    "Multi_Graph_Demand": "https://drive.google.com/file/d/12gZ1XlhU_-1kHufOy8pZtn3CFcIITlrr/view?usp=drive_link",
    "METR_LA": "https://drive.google.com/file/d/1ySgp1I8CdUDEcaJ4PE8m3409AwbIJoen/view?usp=drive_link",
    "M_DENSE": "https://drive.google.com/file/d/1kXHQF6pYLO-iCGMKW6AUkvgY6Vp09N8Z/view?usp=drive_link",
    "LOS_LOOP": "https://drive.google.com/file/d/1SAABiwtpFg7LE70C3jnxW8JckoRk6LoQ/view?usp=drive_link",
    "LOS_LOOP_SMALL": "https://drive.google.com/file/d/1zGWGzHL-hjFJdNPh6EDKjYY1uokmWVQW/view?usp=drive_link",
    "LOOP_SEATTLE": "https://drive.google.com/file/d/1C4zr2Jt4odCziRdKpRUDnxmSlTvn9v50/view?usp=drive_link",
    "instagram": "https://drive.google.com/file/d/1JEkPbQBbrQv8Twe-GzvWUaG7meiimGvT/view?usp=drive_link",
    "HZMETRO": "https://drive.google.com/file/d/1c51xHeaVQcSz2pzjf4GCr8pUHw3Va7jx/view?usp=drive_link",
    "gowalla": "https://drive.google.com/file/d/1c46BRdGEcM4fKiUMrB9zdmjI4uGE2oW6/view?usp=drive_link",
    "Global": "https://drive.google.com/file/d/1wLfGLamS7v9fvdj7uQRudx4Z6Uc3q2oo/view?usp=drive_link",
    "foursquare_tky": "https://drive.google.com/file/d/1-J36AE3DAwsydo8o3TqD41f5NnVd9AgL/view?usp=drive_link",
    "foursquare_nyc": "https://drive.google.com/file/d/1iyf48DIXC9IxI0FrWP8qz7aziWD-63Bx/view?usp=drive_link",
    "CHICAGO_RISK": "https://drive.google.com/file/d/1bQiqlZY07pIGEokxJT2yrxePqUKG77OG/view?usp=drive_link",
    "Chengdu_Taxi_Sample1": "https://drive.google.com/file/d/1P2faZ0lrwpGQ8RMkWYKLnH5OAvaaW3MJ/view?usp=drive_link",
    "brightkite": "https://drive.google.com/file/d/1B4lW_FDkTnTVO4UmYbgAY3qnbmFLCHmX/view?usp=drive_link",
    "bj_roadmap_node": "https://drive.google.com/file/d/1NsaEk-1O4k0pMTWaorodTbIUBRuPqMYf/view?usp=drive_link",
    "bj_roadmap_edge": "https://drive.google.com/file/d/1xihx2_x6MrhxPVbm7h545u1WS5dssqsV/view?usp=drive_link",
    "BIKEDC202007-202009": "https://drive.google.com/file/d/1ZfKDixfRjHzdKJEMDL4UkuXfwCJH_UWV/view?usp=drive_link",
    "BIKECHI202007-202009": "https://drive.google.com/file/d/1MtkDAb9wgBhTEyON7JBchvBtykC6GGib/view?usp=drive_link",
    "BIKECHI202007-202009-3600": "https://drive.google.com/file/d/1Ik1A5fH-GWqwh5A1a3NijvFw9JuB2IYu/view?usp=drive_link",
    "Beijing_Taxi_Sample": "https://drive.google.com/file/d/1LIiXetX7Q8vysVOlgBIwDEFA47y4vBxU/view?usp=drive_link",
    "BEIJING_SUBWAY_30MIN": "https://drive.google.com/file/d/1QHIeZb5vMIK7MY1d3ud02Bc4CgQrw3Kl/view?usp=drive_link",
    "BEIJING_SUBWAY_15MIN": "https://drive.google.com/file/d/1fegnbXO7Fblz3ppSBKMkDoYMoUmJDBC2/view?usp=drive_link",
    "BEIJING_SUBWAY_10MIN": "https://drive.google.com/file/d/1hunTsPUiC_rRdASOHs-PExhPsctvOlGn/view?usp=drive_link",
    "AUSTINRIDE20160701-20160930": "https://drive.google.com/file/d/1-GDS_2k5JHLSPWG95oXm01WoBqAaaiy8/view?usp=drive_link",
}

openai.api_key = API_KEY

# TODO:训练好模型之后替代模型名称
model_name = 'your_gpt_model'


def require(messages):
    '''
    主要函数，通过调用该函数来交互信息
    @param:
        user_content:用户输入的信息,
        exp_id:伴随产生的exp_id，如果为空说明还没有创建，将在本函数中创建实验
    @return:
        exp_id:本次对话产生的exp_id,
        response:GPT的回答
    '''
    completion = openai.ChatCompletion.create(
        model=model_name,
        messages=messages
    )
    response = completion["choices"][0]["message"]["content"]
    return response

def modify_json(user_params, response: str, exp_id: str, user_content: str):
    '''
    将之前的json和获取的信息进行补充，如果任务种类发生了改变，将其他参数进行清空
    @param:
        user_param:之前的json,
        response:GPT分析的文本
    @return:
        merged_param:新的json
    @influence:
        会对之前的json文件进行修改，即，修改数据库
    '''
    content = '请分析这段文字' + user_content + '并生成一个形如' + str(std_json) + '的json信息'  # TODO:增添json格式样例
    content += '只输出json，请不要输出任何其他的自然语言内容'
    completion = openai.ChatCompletion.create(
        model=model_name,
        messages=[
            {"role": "user", "content": content}
        ]
    )
    msg = completion["choices"][0]["message"]["content"]
    msg = msg.remove('`')
    new_param = eval(msg)  # 这里感觉挺有风险的
    new_d = json.loads(new_param)
    user_d = json.loads(user_params)
    if new_d['name'] != user_d['name']:  # 这里是刷新
        write_params(param=new_d, exp_id=exp_id)
        return json(new_d)
    merge_d = {}
    ## 合并json
    for key, value in new_d.items():
        if value != None:
            merge_d[key] = value
        else:
            merge_d[key] = user_d[key]
    has_empty_value = any(value == "" or value is None for value in merge_d.values())
    if not has_empty_value:
        # 执行实验
        # TODO:调用创建执行实验的接口
        write_params(param=merge_d, exp_id=exp_id)
        response += '您的参数已经满足，LibCity-GPT已经为您创建了实验！'
        return json(merge_d)
    else:
        ## 补充缺少的参数
        empty_value_keys = list(all(value == '' or value is None for value in merge_d.values()))
        response += "您目前还缺少"
        for i in len(empty_value_keys):
            response += empty_value_keys[i]
            if i != len(empty_value_keys) - 1:
                response += ','
        response += '的相关参数，请您继续补充~'
        write_params(param=merge_d, exp_id=exp_id)
        return json(merge_d)


def write_params(param, exp_id: str):
    '''
    这个函数主要是将之前的数据库中的json写入
    @param:
        exp_id : 实验名称
    @return:
        无
    '''
    # TODO:将param写入数据库


def legal_check(params):
    """
    这个函数主要是检查用户的参数是否合法
    @param:
        user_params : 用户的参数
    @return:
        bool : 是否合法
    """
    # 判断'实验名称' '所属任务' '模型' '数据集'是否不为空
    if params['task_name'] == '' or params['task'] == '' or params['model'] == '' or params['dataset'] == '':
        return False
    return True
