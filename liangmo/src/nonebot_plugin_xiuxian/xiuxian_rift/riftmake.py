import random, datetime
from datetime import datetime
from .riftconfig import get_config
from ..xiuxian2_handle import OtherSet,XiuxianDateManage
from .jsondata import read_f
from ..read_buff import UserBuffDate, get_main_info_msg, get_sec_msg
from ..xiuxian2_handle import XiuxianDateManage
from ..player_fight import Boss_fight
from ..item_json import Items
from ..xiuxian_config import USERRANK
from ..xiuxian_boss import get_user_boss_fight_info
sql_message = XiuxianDateManage()
items = Items()
skill_data = read_f()

NONEMSG = [
    "道友在秘境中晕头转向，等到清醒时竟然发现已被秘境踢出，毫无所获！",
    "道友进入秘境发现此地烟雾缭绕，无法前行，只能原路而返空手而归！",
]

TREASUREMSG = [
    "道友进入秘境后搜刮了一番，{}",
    "道友进入秘境后竟然发现了一位前辈坐化于此，{}"
]
YLSFMSG = [
    "道友游历四方，在鱼仔码头遇到了海盗袭击当地的渔民，你出手相救，渔民们非常感谢你，赠予你他们在海里捞上来的宝物：{}。本次游历让你受益匪浅，你更加了解这片大陆了，增加{}世界积分，{}灵石，{}修为。",
    "道友游历四方，在河道矿场遇到了苦不堪言的矿工们，你趁夜色潜入矿老板的家中，女人的呻吟声盖过了你的脚步声，只见黑暗中寒光一闪，人头落地，矿工们的脚镣应声而断，矿工们十分感谢你，赠予你挖出来的宝物：{}。本次游历让你受益匪浅，你更加了解这片大陆了，增加{}世界积分，{}灵石，{}修为。",
    "道友游历四方，在凛冬城加入了讨伐异鬼的大军，“长夜将至，我从今开始守望，今夜如此，夜夜皆然”，作为北境的一员大将，国王赏赐了你：{}。本次游历让你受益匪浅，你更加了解这片大陆了，增加{}世界积分，{}灵石，{}修为。",
    "道友游历四方，在无尽沙海遇到了一个迷路的商队，出价50灵石雇佣你当保镖，在他们苦苦哀求下你同意了，一路护送他们走出沙漠，没想到商队首领竟是富甲一方的石油佬，佣人们呈上了你护送商队的报酬：{}。本次游历让你受益匪浅，你更加了解这片大陆了，增加{}世界积分，{}灵石，{}修为。",
    "道友游历四方，路过哥布林洞穴时看到了一位衣衫不整的女骑士，你一怒之下血洗了整个洞穴，出来时却发现女骑士已经不在了，只留下了{}和一份纸条“感谢你为我做的一切，不过我已不再纯洁，除了这些宝物和灵石，无以为报...本次游历让你感到遗憾，你更加痛恨哥布林了，增加{}世界积分，{}灵石，{}修为。",
    "道友游历四方，在巨兽森林里遇到被野兽围攻的豹人族妹子，你手持火把驱散了野兽，豹人妹子将你带回了部落，豹人族热情的招待了你，并让你留在部落，那晚，你们坐在树杈上望向天上的月亮，她给了你一个吻...，你彻夜未眠。可惜爱情终抵不过你对冒险的向往，临行时，她悄悄的把{}塞给了你。本次游历让你怦然心动，你的xp增加了，增加{}世界积分，{}灵石，{}修为。",
    "道友游历四方，在苦啸墓地里遇到了正在哭泣的亡魂，它请求你帮它在墓碑上放一朵鲜花，可是在这凄凉地怎么会有花呢？于是你割开自己的灵脉，借着刺骨的寒风，凝成了一朵冰花，放在了它的墓前，耳旁的哭声似乎减少了些许，亡魂告诉你去墓地深处的一个地方，你在那里拿到了亡魂给你的谢礼：{}。本次游历让你受益匪浅，你更加了解这片大陆了，增加{}世界积分，{}灵石，{}修为。",
    "道友游历四方，在黑水城参加拍卖会，结果价格高的离谱，引起了众人的不满，你到后台一看发现拍卖品都被血狼帮给洗劫了，主持拍卖的是两具尸体制作的人偶，我测，这能忍？你召集众人杀到了血狼帮，一向嚣张跋扈的帮主看到这么多人也不得不变得好说话了起来，没等你回应，一把飞斧便将他劈成了两半，血狼帮从此解散了，你进入他们的营地心满意足的挑了几件宝物：{}。本次游历让你受益匪浅，你更加了解这片大陆了，增加{}世界积分，{}灵石，{}修为。",
    "道友游历四方，来到了被毒品支配的恶沼城，路边的小孩两眼空洞，骨瘦嶙峋，手臂上插着针管，凡是沾了毒品的人都如同陷入这恶沼，你不忍看到他们再这样堕落下去，手起刀落，血流到了毒贩的脚边，他不屑的啐了一口，让你不要坏了他的生意，你念力操动血液，直穿他的头颅，你在毒贩的尸体上搜到了{}。本次游历让你感到痛心，你决心要把毒贩全部正法，增加{}世界积分，{}灵石，{}修为。",
    "道友游历四方，在灵药山遇到了一位正在采药的女子，你正想开口询问，她赶紧转过脸，用面纱紧紧蒙住，一不小心把药材撒了一地，你正想帮她捡起来，不小心碰到她的指尖，然而并没有想象中的温度和触感，而是如臻冰一般让人发寒，原来她得了一种罕见的病，但凡接触到的凡人都无一例外被冻结，她见你竟无事发生，瞪大了双眼，目光犹如冰雪般纯洁。在下山途中，你了解到，她的名字叫雪儿，这种病需要由元婴期以上并且为火属性灵根的修炼者，在8盏炉火中间与其交合，方可彻底治愈，然这灵药山只有两位炼药师是火属性灵根，且修为未达结丹境，说到这里，雪儿望向你的眼神里多了一丝温度，脸上也不禁多了一抹桃红。“灵药山终年积雪，还请道友替人解忧！“雪儿如此说到，你本想拒绝，但一想到这可能是她此生仅有的机会，便答应了下来。在丹炉环绕中，空气都开始摇晃了起来，一冰一火热烈的缠绕着，随着一阵阵热量的注入，寒冰也逐渐消融，你获得了雪儿的谢礼：{}。本次游历让你受益匪浅，你变得更持久了，增加{}世界积分，{}灵石，{}修为。",
    "道友游历四方，在白狼山遇到一只正在被追猎的狼，雪白的狼毛上一道道鲜红的血痕，很明显这只狼命不久矣，你沿着血迹走去，一阵破风声音从耳边划过，转头，一根白羽箭已插入树干半尺。“你是哪里来的野人？为什么要来这里？这里很危险你不知道吗！”你往声音的方向看去，一个猎人打扮的男子正持弓对着你。他身披白色狼皮，材质与刚才将死的那只狼一致。这个男人叫半账，是白狼山的守山猎户，传说初代猎人使用猎弓，配合初代白狼王，击杀了来犯的异兽，而鹿首精是最强大的一个，在初代猎户将其击杀后将尸体封印在这白鹿山，自己也驾鹤西去，谁知这狡猾的异兽藏在地底下，暗中杀死了白狼的后代，而白狼一旦灭绝，鹿首精将重返人间，半账此行便是来讨伐鹿首精。白狼已死，黑夜将至，正在你们谈话时，瞬间乌云密布，漫天的乌鸦往山顶聚集，这是鹿首精要复活的征兆，你和半账迅速往山顶跑去，你近身跟它缠斗，半账在远处射箭，就这样打了七天七夜，终于将它压制，最终唤醒白狼之灵，将其魂魄彻底吞噬。在完成这一切后，你们瘫软在地，望着天上的乌云渐渐散开，晨曦又一次拥抱白狼山，你收到了半账的谢礼：{}。本次游历让你受益匪浅，你更加了解这片大陆了，增加{}世界积分，{}灵石，{}修为。"
]
TIME = {
    "10800",
    "14400",
    "18000",
    "21600"
}

YLSFGET = {
    "宝物":{
        "type_rate":300,
        "功法":{
            "type_rate":100,
        },
        "神通":{
            "type_rate":100,
        },
        "法器":{
            "type_rate":50,
        },
        "防具":{
            "type_rate":50,
        }
    }
}

STORY = {
    "宝物":{
        "type_rate":300,
        "功法":{
            "type_rate":50,
        },
        "神通":{
            "type_rate":50,
        },
        "法器":{
            "type_rate":50,
        },
        "防具":{
            "type_rate":50,
        },
        "灵石":{
            "type_rate":100,
            "stone":5000
        }
    },
    "战斗":{
        "type_rate":100,
        "Boss战斗":{
            "type_rate":200,
            "Boss数据":{
                "name":["墨蛟","婴鲤兽","千目妖","鸡冠蛟","妖冠蛇","铁火蚁","天晶蚁","银光鼠","紫云鹰","狗青"],
                "hp":[1.2, 1.4, 1.6, 1.8, 2, 3],
                "mp":10,
                "atk":[0.1, 0.12, 0.14, 0.16, 0.18, 0.5],
                "shuxing":["金","木","水","火","土","光","暗"]
            },
            "success":{
                "desc":"道友大战一番成功战胜{}!",
                "give":{
                    "exp":[0.01, 0.02, 0.03, 0.04, 0.05],
                    "stone":5000
                }
            },
            "fail":{
                "desc":"道友大战一番不敌{}，仓皇逃窜！",
            }
        },
        "掉血事件":{
            "type_rate":50,
            "desc":[
                "秘境内竟然散布着浓烈的毒气，道友贸然闯入！{}！",
                "秘境内竟然藏着一群未知势力，道友被打劫了！{}！"
                ],
            "cost":{
                "exp":{
                    "type_rate":50,
                    "value":[0.01, 0.02, 0.03]
                },
                "hp":{
                    "type_rate":100,
                    "value":[0.1, 0.2, 0.3]
                },
                "stone":{
                    "type_rate":50,
                    "value":[5000, 10000, 15000]
                },
            }
        },
    },
    "无事":{
        "type_rate":50,
    }
}


async def get_boss_battle_info(user_info, rift_rank, bot_id):
    """获取Boss战事件的内容"""
    boss_data = STORY['战斗']['Boss战斗']["Boss数据"]
    player = {"user_id": None, "道号": None, "气血": None, "攻击": None, "真元": None, '会心': None, '防御': 0}
    userinfo = sql_message.get_user_real_info(user_info.user_id)
    user1_weapon_data = UserBuffDate(user_info.user_id).get_user_weapon_data()
    if user1_weapon_data != None:
        player['会心'] = int(user1_weapon_data['crit_buff'] * 100)
    else:
        player['会心'] = 1
        
    player['user_id'] = userinfo.user_id
    player['道号'] = userinfo.user_name
    player['气血'] = userinfo.hp
    player['攻击'] = userinfo.atk
    player['真元'] = userinfo.mp
    player['exp'] = userinfo.exp
    
    base_exp = userinfo.exp
    boss_info = {"name": None, "气血": None, "攻击": None, "真元": None, "shuxing": None, 'stone':1}
    boss_info["name"] = random.choice(boss_data["name"])
    boss_info["气血"] = int(base_exp * random.choice(boss_data["hp"]))
    boss_info["攻击"] = int(base_exp * random.choice(boss_data["atk"]))
    boss_info["真元"] = base_exp * boss_data["mp"]
    boss_info["shuxing"] = random.choice(boss_data["shuxing"])
    
    result, victor, bossinfo_new, stone = await Boss_fight(player, boss_info, bot_id=bot_id) #未开启，1不写入，2写入

    if victor == "群友赢了":#获胜
        user_rank = 110 - USERRANK[user_info.level]#50-用户当前等级
        success_info = STORY['战斗']['Boss战斗']["success"]
        msg = success_info['desc'].format(boss_info["name"])
        give_exp = int(random.choice(success_info["give"]["exp"]) * user_info.exp)
        give_stone = (rift_rank + user_rank) * success_info["give"]["stone"]
        sql_message.update_exp(user_info.user_id, give_exp)
        sql_message.update_ls(user_info.user_id, give_stone, 1)#负数也挺正常
        msg += f"获得了修为：{give_exp}点，灵石：{give_stone}枚！"
    else:#输了
        fail_info = STORY['战斗']['Boss战斗']["fail"]
        msg = fail_info['desc'].format(boss_info["name"])
    return result, msg


def get_dxsj_info(rift_type, user_info):
    """获取掉血事件的内容"""
    battle_data = STORY['战斗']
    cost_type = get_dict_type_rate(battle_data[rift_type]['cost'])
    value = random.choice(battle_data[rift_type]['cost'][cost_type]['value'])
    if cost_type == "exp":
        exp = int(user_info.exp * value)
        sql_message.update_j_exp(user_info.user_id, exp)
        
        nowhp = user_info.hp - (exp / 2) if (user_info.hp - (exp / 2)) > 0 else 1
        nowmp = user_info.mp - exp if (user_info.mp - exp) > 0 else 1
        sql_message.update_user_hp_mp(user_info.user_id, nowhp, nowmp)  # 修为掉了，血量、真元也要掉
        
        msg = random.choice(battle_data[rift_type]['desc']).format(f"修为减少了：{exp}点！=")
    elif cost_type == "hp":
        cost_hp = int((user_info.exp / 2) * value)
        now_hp = user_info.hp - cost_hp
        if now_hp < 0:
            now_hp = 1
        sql_message.update_user_hp_mp(user_info.user_id, now_hp, user_info.mp)
        msg = random.choice(battle_data[rift_type]['desc']).format(f"气血减少了：{cost_hp}点！")
    elif cost_type == "stone":
        cost_stone = value
        sql_message.update_ls(user_info.user_id, cost_stone, 2)#负数也挺正常
        msg = random.choice(battle_data[rift_type]['desc']).format(f"灵石减少了：{cost_stone}枚！")
    return msg

def get_ylsf_treasure_info(user_info):
    ylsf_type = get_goods_type_ylsf()
    stone = 10 * (100 - USERRANK[user_info.level])* random.randint(1, 100) * user_info.ylsf  // 3600
    exp = 10 * (100 - USERRANK[user_info.level]) * random.randint(1, 100) * user_info.ylsf  // 3600
    sjjf = 2 * int((100- USERRANK[user_info.level])// 10) * user_info.ylsf  // 7200

    if ylsf_type == "法器":
        weapon_info = get_weapon_ylsf(user_info)
        tmsg = f"{weapon_info[1]['level']}：{weapon_info[1]['name']}"
        msg = random.choice(YLSFMSG).format(tmsg,sjjf,stone,exp)
        sql_message.send_back(user_info.user_id,weapon_info[0],weapon_info[1]['name'], weapon_info[1]['type'],1)
        sql_message.update_ls(user_info.user_id,stone,1)
        sql_message.update_exp(user_info.user_id,exp)
        user_boss_fight_info = get_user_boss_fight_info(user_info.user_id)
        user_boss_fight_info['boss_integral'] += sjjf

    elif ylsf_type == "防具":
        armor_info = get_armor_ylsf(user_info)
        tmsg = f"{armor_info[1]['level']}防具：{armor_info[1]['name']}"
        msg = random.choice(YLSFMSG).format(tmsg,sjjf,stone,exp)
        sql_message.send_back(user_info.user_id, armor_info[0], armor_info[1]['name'], armor_info[1]['type'], 1)
        sql_message.update_ls(user_info.user_id,stone,1)
        sql_message.update_exp(user_info.user_id,exp)
        user_boss_fight_info = get_user_boss_fight_info(user_info.user_id)
        user_boss_fight_info['boss_integral'] += sjjf
        
    elif ylsf_type == "神通":
        st_info = get_st_ylsf(user_info)
        tmsg = f"{st_info[1]['level']}神通：{st_info[1]['name']}"
        msg = random.choice(YLSFMSG).format(tmsg,sjjf,stone,exp)
        sql_message.send_back(user_info.user_id, st_info[0], st_info[1]['name'], st_info[1]['type'], 1)
        sql_message.update_ls(user_info.user_id,stone,1)
        sql_message.update_exp(user_info.user_id,exp)
        user_boss_fight_info = get_user_boss_fight_info(user_info.user_id)
        user_boss_fight_info['boss_integral'] += sjjf

    elif ylsf_type == "功法":
        gf_info = get_gf_ylsf(user_info)
        tmsg = f"{gf_info[1]['level']}功法：{gf_info[1]['name']}"
        msg = random.choice(YLSFMSG).format(tmsg,sjjf,stone,exp) 
        sql_message.send_back(user_info.user_id, gf_info[0], gf_info[1]['name'], gf_info[1]['type'], 1)
        sql_message.update_ls(user_info.user_id,stone,1)
        sql_message.update_exp(user_info.user_id,exp)
        user_boss_fight_info = get_user_boss_fight_info(user_info.user_id)
        user_boss_fight_info['boss_integral'] += sjjf
    
    return msg


def get_treasure_info(user_info, rift_rank):
    rift_type = get_goods_type()#功法、神通、法器、防具、法宝#todo
    
    if rift_type == "法器":
        weapon_info = get_weapon(user_info, rift_rank)
        temp_msg = f"竟然获得了{weapon_info[1]['level']}：{weapon_info[1]['name']}！"
        msg = random.choice(TREASUREMSG).format(temp_msg)
        sql_message.send_back(user_info.user_id, weapon_info[0], weapon_info[1]['name'], weapon_info[1]['type'], 1)
        #背包sql
        
    elif rift_type == "防具":#todo
        armor_info = get_armor(user_info, rift_rank)
        temp_msg = f"竟然获得了{armor_info[1]['level']}防具：{armor_info[1]['name']}！"
        msg = random.choice(TREASUREMSG).format(temp_msg)
        sql_message.send_back(user_info.user_id, armor_info[0], armor_info[1]['name'], armor_info[1]['type'], 1)
        #背包sql
        
    elif rift_type == "功法":
        give_main_info = get_main_info(user_info.level, rift_rank)
        if give_main_info[0]:#获得了
            main_buff_id = give_main_info[1]
            main_buff = items.get_data_by_item_id(main_buff_id)
            temp_msg = f"竟然获得了{main_buff['level']}功法：{main_buff['name']}！"
            msg = random.choice(TREASUREMSG).format(temp_msg)
            sql_message.send_back(user_info.user_id, main_buff_id, main_buff['name'], main_buff['type'], 1)
        else:
            msg = '竟空手而归！'
        
    elif rift_type == "神通":
        give_sec_info = get_sec_info(user_info.level, rift_rank)
        if give_sec_info[0]:#获得了
            sec_buff_id = give_sec_info[1]
            sec_buff = items.get_data_by_item_id(sec_buff_id)
            temp_msg = f"竟然获得了{sec_buff['level']}功法：{sec_buff['name']}！"
            msg = random.choice(TREASUREMSG).format(temp_msg)
            sql_message.send_back(user_info.user_id, sec_buff_id, sec_buff['name'], sec_buff['type'], 1)
            #背包sql
        else:
            msg = '竟空手而归！'
    
    elif rift_type == "灵石":
        stone_base = STORY['宝物']['灵石']['stone']
        user_rank = 110 - USERRANK[user_info.level]#50-用户当前等级
        give_stone = (rift_rank + user_rank) * stone_base
        sql_message.update_ls(user_info.user_id, give_stone, 1)
        temp_msg = f"竟然获得了灵石：{give_stone}枚！"
        msg = random.choice(TREASUREMSG).format(temp_msg)
    
    return msg

def get_dict_type_rate(data_dict):
    """根据字典内概率，返回字典key"""
    temp_dict = {}
    for i, v in data_dict.items():
        try:
            temp_dict[i] = v["type_rate"]
        except:
            continue
    key = OtherSet().calculated(temp_dict)
    return key

def get_rift_type():
    """根据概率返回秘境等级"""
    data_dict = get_config()['rift']
    return get_dict_type_rate(data_dict)

def get_story_type():
    """根据概率返回事件类型"""
    data_dict = STORY
    return get_dict_type_rate(data_dict)

def get_battle_type():
    """根据概率返回战斗事件的类型"""
    data_dict = STORY['战斗']
    return get_dict_type_rate(data_dict)

def get_goods_type():
    data_dict = STORY['宝物']
    return get_dict_type_rate(data_dict)

def get_goods_type_ylsf():
    data_dict = YLSFGET['宝物']
    return get_dict_type_rate(data_dict)

def get_id_by_rank(dict_data, user_level, rift_rank=0):
    """根据字典的rank、用户等级、秘境等级随机获取key"""
    l_temp = []
    final_rank = USERRANK[user_level] - rift_rank #秘境等级，会提高用户的等级
    pass_rank = 6 #最终等级超过次等级会抛弃
    for k, v in dict_data.items():
        if v["rank"] >= final_rank and (v["rank"] - final_rank) <= pass_rank:
            l_temp.append(k)
            
    return random.choice(l_temp)

def get_id_by_rank_ylsf(dict_data, user_level):
    """根据字典的rank、用户等级随机获取key"""
    l_temp = []
    final_rank = USERRANK[user_level] + 6 
    pass_rank = 3
    for k, v in dict_data.items():
        if (int(v["rank"]) - final_rank) <= pass_rank:
            l_temp.append(k)
            
    return random.choice(l_temp)

def get_weapon_ylsf(user_info):
    """随机获取法器，游历四方"""
    weapon_data = items.get_data_by_item_type(['法器'])
    weapon_id = get_id_by_rank_ylsf(weapon_data,user_info.level)
    weapon_info = items.get_data_by_item_id(weapon_id)
    return weapon_id,weapon_info

def get_armor_ylsf(user_info):
    """随机获取防具，游历四方"""
    armor_data = items.get_data_by_item_type(['防具'])
    armor_id = get_id_by_rank_ylsf(armor_data,user_info.level)
    armor_info = items.get_data_by_item_id(armor_id)
    return armor_id,armor_info

def get_st_ylsf(user_info):
    """随机获得神通，游历四方"""
    st_data = items.get_data_by_item_type(['神通'])
    st_id = get_id_by_rank_ylsf(st_data,user_info.level)
    st_info = items.get_data_by_item_id(st_id)
    return st_id,st_info

def get_gf_ylsf(user_info):
    """ 随机获取功法"""
    gf_data = items.get_data_by_item_type(['功法'])
    gf_id = get_id_by_rank_ylsf(gf_data,user_info.level)
    gf_info = items.get_data_by_item_id(gf_id)
    return gf_id, gf_info

def get_weapon(user_info, rift_rank=0):
    """
    随机获取一个法器
    :param user_info：用户信息类
    :param rift_rank：秘境等级
    :return 法器ID, 法器信息json
    """
    weapon_data = items.get_data_by_item_type(['法器'])
    weapon_id = get_id_by_rank(weapon_data, user_info.level, rift_rank)
    weapon_info = items.get_data_by_item_id(weapon_id)
    return weapon_id, weapon_info

def get_armor(user_info, rift_rank=0):
    """
    随机获取一个防具
    :param user_info：用户信息类
    :param rift_rank：秘境等级
    :return 防具ID, 防具信息json
    """
    armor_data = items.get_data_by_item_type(['防具'])
    armor_id = get_id_by_rank(armor_data, user_info.level, rift_rank)
    armor_info = items.get_data_by_item_id(armor_id)
    return armor_id, armor_info

def get_main_info(user_level, rift_rank):
    """获取功法的信息"""
    user_rank = USERRANK[user_level] #type=int，用户等级
    main_buff_type = get_skill_by_rank(user_level, rift_rank)#天地玄黄
    main_buff_id_list = skill_data[main_buff_type]['gf_list']
    init_rate = 60 #初始概率为60
    finall_rate = init_rate + rift_rank * 5
    finall_rate = finall_rate if finall_rate <= 100 else 100
    is_success = False
    main_buff_id = 0
    if random.randint(0, 100) <= finall_rate: #成功
        is_success = True
        main_buff_id = random.choice(main_buff_id_list)
        return is_success, main_buff_id
    return is_success, main_buff_id

def get_sec_info(user_level, rift_rank):
    """获取神通的信息"""
    user_rank = USERRANK[user_level] #type=int，用户等级
    sec_buff_type = get_skill_by_rank(user_level, rift_rank)#天地玄黄
    sec_buff_id_list = skill_data[sec_buff_type]['st_list']
    init_rate = 60 #初始概率为60
    finall_rate = init_rate + rift_rank * 5
    finall_rate = finall_rate if finall_rate <= 100 else 100
    is_success = False
    sec_buff_id = 0
    if random.randint(0, 100) <= finall_rate: #成功
        is_success = True
        sec_buff_id = random.choice(sec_buff_id_list)
        return is_success, sec_buff_id
    return is_success, sec_buff_id

def get_skill_by_rank(user_level, rift_rank):
    """根据用户等级、秘境等级随机获取一个技能"""
    user_rank = USERRANK[user_level]#type=int，用户等级
    temp_dict = []
    for k, v in skill_data.items():
        if user_rank - rift_rank <= v['rank']:  #秘境等级会增幅用户等级
            temp_dict.append(k)
    return random.choice(temp_dict)

def check_ylsf(user_id, needtime):
    """检查游历四方cd"""
    now = datetime.now()
    user_message = sql_message.get_user_message(user_id)
    ylsf_cd = user_message.ylsf_cd
    if ylsf_cd:
        time =OtherSet().date_diff(now,ylsf_cd)
        leftime = needtime - time
        if  time < needtime:
            is_time = False
            msg = "道友正在进行一场云游哦，请{}分钟后再来吧".format(leftime // 60)
            return is_time, msg
        else:
            is_time = True
            return is_time

class Rift:
    def __init__(self) -> None:
        self.name = ''
        self.rank = 0
        self.count = 0
        self.l_user_id = []
        self.time = 0
        
