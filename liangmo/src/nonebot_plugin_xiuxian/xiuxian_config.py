
from pathlib import Path
import json
import yaml

DATABASE = Path() / "data" / "xiuxian"

class XiuConfig:

    def __init__(self):
        self.config_yamlpath = DATABASE / "config.yaml"
        config_data = self._config_data()

        self.level = config_data['level']
        self.level_up_cd = config_data["level_up_cd"]  # 境界突破CD 单位分钟
        self.hf_cd = config_data["hf_cd"]  # 护法cd 单位分钟
        self.sx_base_exp = config_data["sx_base_exp"] #双修基础获得修为
        self.reuse_ls = config_data["reuse_ls"]  # 灵石回收价
        self.cost_exp_need_upline = config_data["cost_exp_need_upline"]  # 被罚修为上限
        self.cost_exp_need_downline = config_data["cost_exp_need_downline"] # 被罚修为下限
        self.closing_exp = config_data['closing_exp']  # 闭关每分钟增加的修为
        self.closing_exp_upper_limit = config_data['closing_exp_upper_limit']  # 闭关可获取修为上限（下一个境界需要的修为的1.5倍）
        self.level_punishment_floor = config_data['level_punishment_floor']  # 突破失败扣除修为，惩罚下限(当前实例：1%)
        self.level_punishment_limit = config_data['level_punishment_limit']  # 突破失败扣除修为，惩罚上限(当前实例：10%)
        self.level_up_probability = config_data['level_up_probability']  # 突破失败增加当前境界突破概率的比例
        self.sign_in_lingshi_lower_limit = config_data['sign_in_lingshi_lower_limit']  # 每日签到灵石下限
        self.sign_in_lingshi_upper_limit = config_data['sign_in_lingshi_upper_limit']  # 每日签到灵石上限
        self.sign_in_xiuwei_lower_limit = config_data['sign_in_xiuwei_lower_limit']  # 每日签到修为下限
        self.sign_in_xiuwei_upper_limit = config_data['sign_in_xiuwei_upper_limit']  # 每日签到修为上限
        self.tou = config_data['tou']  # 偷灵石惩罚
        self.tou_lower_limit = config_data['tou_lower_limit']  # 偷灵石下限
        self.tou_upper_limit = config_data['tou_upper_limit']  # 偷灵石上限
        self.remake = config_data['remake']  # 重入仙途的消费
        self.sect_min_level = config_data['sect_min_level']  # 创建宗门的最低修为等级要求
        self.sect_create_cost = config_data['sect_create_cost']  # 创建宗门的最低修为等级要求
        self.user_info_cd = config_data['user_info_cd']  # 我的修仙信息查询cd
        self.user_info_cd_msg = config_data['user_info_cd_msg']
        self.dufang_cd = config_data['dufang_cd']  # 金银阁cd
        self.dufang_cd_msg = config_data['dufang_cd_msg']
        self.tou_cd = config_data['tou_cd']  # 偷灵石CD
        self.fuck = config_data['fuck']
        self.fuck_cd = config_data['fuck_cd']
        self.fuck_lower_limit = config_data['fuck_lower_limit']
        self.fuck_upper_limit = config_data['fuck_upper_limit']
        self.huifu_cd = config_data['huifu_cd']
        # self.ggg = config_data['ggg']

        self.sql_table = ["user_xiuxian", "user_cd", "sects", "back", "BuffInfo"]  # 数据库表校验
        self.sql_user_xiuxian = ["level_up_rate", "sect_id", "sect_position", "hp", "mp", "atk", "atkpractice",
                           "sect_task", "sect_contribution", "sect_elixir_get", "blessed_spot_flag", "blessed_spot_name"]  # 数据库字段校验
        self.sql_sects = ["sect_materials", "mainbuff", "secbuff", "elixir_room_level"]
        self.sql_buff = ["armor_buff", "atk_buff", "blessed_spot"]
        self.sql_back = ["bind_num"]
        self.img = True #是否全部转为简单图片发送

        # sql_table: ["user_xiuxian", "user_cd", "sects", "back", "BuffInfo"]  # 数据库表校验
        # sql_user_xiuxian: ["level_up_rate", "sect_id", "sect_position", "hp", "mp", "atk", "atkpractice",
        #                    "sect_task"]  # 数据库字段校验
        # sql_sects: ["sect_materials", "mainbuff", "secbuff"]

    def _config_data(self):
        """配置数据"""
        with open(self.config_yamlpath, 'r', encoding='utf-8') as e:
            a = e.read()
            data = yaml.safe_load(a)
            return data


class JsonConfig:
    def __init__(self):
        self.config_jsonpath = DATABASE / "config.json"


    def read_data(self):
        """配置数据"""
        with open(self.config_jsonpath, 'r', encoding='utf-8') as e:
            data = json.load(e)
            return data

    def write_data(self, key, group_id=None):
        """
        说明：设置抢灵石开启或关闭
        参数：
            key：抢灵石1为开启，2为关闭
            key: 群聊1为开启，2为关闭
        """

        json_data = self.read_data()

        if key == 1:
            json_data['qiang'] = True
        if key == 2:
            json_data['qiang'] = False

        if key == 3 or key == 4:
            try:
                dd = json_data['group']
                if key == 4:
                    dd.append(group_id)
                if key == 3:
                    try:
                        dd.remove(group_id)
                    except ValueError:
                        print('删除数据失败')
                        return False
            except KeyError:
                json_data['group'] = [group_id]

        with open(self.config_jsonpath, 'w', encoding='utf-8') as f:
            json.dump(json_data, f)

USERRANK = {
    '江湖好手':100,
    '练气境初期':99,
    '练气境中期':98,
    '练气境圆满':97,
    '筑基境初期':96,
    '筑基境中期':95,
    '筑基境圆满':94,
    '结丹境初期':93,
    '结丹境中期':92,
    '结丹境圆满':91,
    '元婴境初期':90,
    '元婴境中期':89,
    '元婴境圆满':88,
    '化神境初期':87,
    '化神境中期':86,
    '化神境圆满':85,
    '炼虚境初期':84,
    '炼虚境中期':83,
    '炼虚境圆满':82,
    '合体境初期':81,
    '合体境中期':80,
    '合体境圆满':79,
    '大乘境初期':78,
    '大乘境中期':77,
    '大乘境圆满':76,
    '渡劫境初期':75,
    '渡劫境中期':74,
    '渡劫境圆满':73,
    '半步真仙':72,
    '真仙境初期':71,
    '真仙境中期':70,
    '真仙境圆满':69,
    '金仙境初期':68,
    '金仙境中期':67,
    '金仙境圆满':66,
    '太乙境初期':65,
    '太乙境中期':64,
    '太乙境圆满':63,
    '大罗境初期':62,
    '大罗境中期':61,
    '大罗境圆满':60,
    '道祖境初期':59,
    '道祖境中期':58,
    '道祖境圆满':57,
    '道尊境初期':56,
    '道尊境中期':55,
    '道尊境圆满':54,
    '道仙境初期':53,
    '道仙境中期':52,
    '道仙境圆满':51,
    '天道主宰':50,
}

if __name__ == '__main__':
    pathname = r""
    with open(pathname, 'r', encoding='utf-8') as e:
        data = json.load(e)

    key = 4


    if key == 1:
        data['qiang'] = True
    if key == 2:
        data['qiang'] = False
    if key == 3 or key == 4:
        try:
            dd = data['group']
            if key == 3:
                dd.append('223')
            if key == 4:
                try:
                    dd.remove('123')
                except ValueError:
                    print('bbbb')
        except KeyError:
            data['group'] = []

    with open(pathname, 'w', encoding='utf-8') as f:
        json.dump(data, f)