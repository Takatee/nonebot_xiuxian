import random
import re
from datetime import datetime

from .help import *
from nonebot import get_driver
from nonebot import require
from nonebot.adapters.onebot.v11 import (
    PRIVATE_FRIEND,
    Bot,
    GROUP,
    Message,
    MessageEvent,
    GroupMessageEvent,
    MessageSegment,
)
from nonebot.log import logger
from typing import Any, Tuple
from nonebot.params import CommandArg, RegexGroup, EventPlainText

from .command import *
from .cd_manager import add_cd, check_cd, cd_msg
from .data_source import jsondata
from .xiuxian2_handle import XiuxianDateManage, XiuxianJsonDate, OtherSet
from .xiuxian_config import XiuConfig, JsonConfig
from .xiuxian_opertion import do_is_work
from .read_buff import UserBuffDate
from .utils import Txt2Img, data_check_conf, check_user_type, get_msg_pic, check_user
from .item_json import Items
from .read_buff import get_player_info, save_player_info



# 定时任务
scheduler = require("nonebot_plugin_apscheduler").scheduler

driver = get_driver()
work = {}  # 悬赏令信息记录
sect_out_check = {}  # 退出宗门或踢出宗门信息记录
sql_message = XiuxianDateManage()  # sql类

from nonebot import load_all_plugins
src = 'src.plugins.'
load_all_plugins(
        [
            f'{src}nonebot_plugin_xiuxian.xiuxian_boss',
            f'{src}nonebot_plugin_xiuxian.xiuxian_bank',
            f'{src}nonebot_plugin_xiuxian.xiuxian_sect',
            f'{src}nonebot_plugin_xiuxian.xiuxian_info',
            f'{src}nonebot_plugin_xiuxian.xiuxian_buff',
            f'{src}nonebot_plugin_xiuxian.xiuxian_back',
            f'{src}nonebot_plugin_xiuxian.xiuxian_rift',
            f'{src}nonebot_plugin_xiuxian.xiuxian_mixelixir',
            f'{src}nonebot_plugin_xiuxian.xiuxian_work',
        ],
        [],
    )

@command.ls_update_hp_mp.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """灵石恢复状态"""
    await data_check_conf(bot, event)

    try:
        user_id, group_id, mess = await data_check(bot, event)
    except MsgError:
        return

    if cd := check_cd(event, '恢复状态'):
        # 如果 CD 还没到 则直接结束
        await dufang.finish(f"@{event.sender.nickname}" + cd_msg(cd))

    add_cd(event, XiuConfig().huifu_cd, '恢复状态')
    user_id = event.get_user_id()
    user_message = sql_message.get_user_message(user_id)
    if user_message.hp == (user_message.exp / 2)  and  user_message.mp == user_message.exp:
        msg = "{}道友的状态目前良好，不需要恢复状态哦！"
        if XiuConfig().img:
            pic = await get_msg_pic(msg)
            await ls_update_hp_mp.finish(MessageSegment.image(pic))
        else:
            await ls_update_hp_mp.finish(msg)


    basestone = 10
    user_old_hp = user_message.hp
    user_old_mp = user_message.mp
    user_now_hp = user_message.exp / 2
    user_now_mp = user_message.exp
    update_hp = user_now_hp - user_old_hp
    update_mp = user_now_mp - user_old_mp
    gain_zt = update_hp + update_mp
    ls_stone = int(gain_zt * basestone * 0.005)
    if ls_stone > user_message.stone:
        sql_message.update_user_hp_mp(user_id,user_old_hp,user_old_mp)
        msg = "{}道友的灵石还不够支持您恢复至满血量哦~".format(user_message.user_name)
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await ls_update_hp_mp.finish(MessageSegment.image(pic))
        else:
            await ls_update_hp_mp.finish(f"@{event.sender.nickname}" + msg)
    sql_message.update_power2(user_id)  # 更新战力
    sql_message.update_user_hp(user_id)
    sql_message.update_ls(user_id,ls_stone,2)
    msg = "{}道友使用{}枚灵石恢复自身血量和真元，状态已经恢复至100%".format(user_message.user_name,ls_stone)
    if XiuConfig().img:
        pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
        await ls_update_hp_mp.finish(MessageSegment.image(pic))
    else:
        await ls_update_hp_mp.finish(f"@{event.sender.nickname}" + msg)

@command.run_xiuxian.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """加入修仙"""
    await data_check_conf(bot, event)

    user_id = event.get_user_id()
    user_name = (
        event.sender.card if event.sender.card else event.sender.nickname
    )  # 获取为用户名
    root, root_type = XiuxianJsonDate().linggen_get()  # 获取灵根，灵根类型

    rate = sql_message.get_root_power_rate(root_type)  # 灵根倍率
    power = 100 * float(rate)  # 战力=境界的power字段 * 灵根的rate字段
    create_time = str(datetime.now())

    msg = sql_message.create_user(
        user_id, root, root_type, int(power), create_time, user_name
    )
    if XiuConfig().img:
        pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
        await run_xiuxian.finish(MessageSegment.image(pic))
    else:
        await run_xiuxian.finish(f"@{event.sender.nickname}" + msg)


@sign_in.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """修仙签到"""
    await data_check_conf(bot, event)

    try:
        user_id, group_id, mess = await data_check(bot, event)
    except MsgError:
        return

    result = sql_message.get_sign(user_id)
    sql_message.update_power2(user_id)
    if XiuConfig().img:
        pic = await get_msg_pic(f"@{event.sender.nickname}" + result)
        await sign_in.finish(MessageSegment.image(pic))
    else:
        await sign_in.finish(f"@{event.sender.nickname}" + result)


@command.help_in.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """修仙帮助"""
    await data_check_conf(bot, event)

    font_size = 30
    title = '修仙模拟器帮助信息'
    msg = help.__xiuxian_notes__
    img = Txt2Img(font_size)
    pic = img.save(title, msg)
    await help_in.send(MessageSegment.image(pic))
#     msg = help.__xiuxian_notes__
#     await help_in.send(msg)

@command.help_strategy.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """修仙攻略"""
    await data_check_conf(bot, event)

    font_size = 30
    title = '修仙攻略'
    msg = help.__xiuxian_strategy__
    img = Txt2Img(font_size)
    pic = img.save(title, msg)
    await help_strategy.send(MessageSegment.image(pic))

@command.dufang.handle()
async def _(bot: Bot, event: MessageEvent, args: Tuple[Any, ...] = RegexGroup()):
    await data_check_conf(bot, event)

    try:
        user_id, group_id, mess = await data_check(bot, event)
    except MsgError:
        return

    if cd := check_cd(event, '金银阁'):
        # 如果 CD 还没到 则直接结束
        await dufang.finish(f"@{event.sender.nickname}" + cd_msg(cd))

    user_message = sql_message.get_user_message(user_id)

    add_cd(event, XiuConfig().dufang_cd, '金银阁')

    if args[2] is None:
        msg = f"请输入正确的指令，例如金银阁10大、金银阁10奇、金银阁10猜3"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await dufang.finish(MessageSegment.image(pic))
        else:
            await dufang.finish(f"@{event.sender.nickname}" + msg)
        

    price = args[1]  # 300
    mode = args[2]  # 大、小、奇、偶、猜
    mode_num = 0
    if mode == '猜':
        mode_num = args[3]  # 猜的数值
        if str(mode_num) not in ['1', '2', '3', '4', '5', '6']:
            msg = f"请输入正确的指令，例如金银阁10大、、金银阁10奇、金银阁10猜3"
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                await dufang.finish(MessageSegment.image(pic))
            else:
                await dufang.finish(f"@{event.sender.nickname}" + msg)

    price_num = int(price)
    if int(user_message.stone) < price_num:
        msg = "道友的金额不足，请重新输入！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await dufang.finish(MessageSegment.image(pic))
        else:
            await dufang.finish(f"@{event.sender.nickname}" + msg)
    elif price_num == 0:
        msg = "走开走开，0块钱也赌！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await dufang.finish(MessageSegment.image(pic))
        else:
            await dufang.finish(f"@{event.sender.nickname}" + msg)

    value = random.randint(1, 6)
    msg = Message("[CQ:dice,value={}]".format(value))

    if value >= 4 and str(mode) == "大":
        sql_message.update_ls(user_id, price_num, 1)
        await dufang.send(msg)
        msg = "最终结果为{}，你猜对了，收获灵石{}块".format(value, price_num)
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await dufang.finish(MessageSegment.image(pic))
        else:
            await dufang.finish(f"@{event.sender.nickname}" + msg)
        
    elif value <= 3 and str(mode) == "小":
        sql_message.update_ls(user_id, price_num, 1)
        await dufang.send(msg)
        msg = "最终结果为{}，你猜对了，收获灵石{}块".format(value, price_num)
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await dufang.finish(MessageSegment.image(pic))
        else:
            await dufang.finish(f"@{event.sender.nickname}" + msg)
    elif value %2==1 and str(mode) == "奇":
        sql_message.update_ls(user_id, price_num, 1)
        await dufang.send(msg)
        msg = "最终结果为{}，你猜对了，收获灵石{}块".format(value, price_num)
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await dufang.finish(MessageSegment.image(pic))
        else:
            await dufang.finish(f"@{event.sender.nickname}" + msg)
    elif value %2==0 and str(mode) == "偶":
        sql_message.update_ls(user_id, price_num, 1)
        await dufang.send(msg)
        msg = "最终结果为{}，你猜对了，收获灵石{}块".format(value, price_num)
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await dufang.finish(MessageSegment.image(pic))
        else:
            await dufang.finish(f"@{event.sender.nickname}" + msg)

    elif str(value) == str(mode_num) and str(mode) == "猜":
        sql_message.update_ls(user_id, price_num * 5, 1)
        await dufang.send(msg)
        msg = "最终结果为{}，你猜对了，收获灵石{}块".format(value, price_num * 5)
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await dufang.finish(MessageSegment.image(pic))
        else:
            await dufang.finish(f"@{event.sender.nickname}" + msg)

    else:
        sql_message.update_ls(user_id, price_num, 2)
        await dufang.send(msg)
        msg = "最终结果为{}，你猜错了，损失灵石{}块".format(value, price_num)
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await dufang.finish(MessageSegment.image(pic))
        else:
            await dufang.finish(f"@{event.sender.nickname}" + msg)


@command.restart.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """重置灵根信息"""
    await data_check_conf(bot, event)

    try:
        user_id, group_id, mess = await data_check(bot, event)
    except MsgError:
        return

    # 境界为练气期才能重置灵根
    mess = sql_message.get_user_message(user_id)
    if mess.level !="练气境初期" and mess.level !="练气境中期" and mess.level !="练气境圆满" and mess.level !="江湖好手":
        name, root_type = XiuxianJsonDate().linggen_get()
        result = sql_message.ramaker(name, root_type, user_id)
        
        sql_message.update_user_helf_exp(user_id)  # 经验减半

        sql_message.update_power2(user_id)  # 更新战力
        sql_message.update_user_hp(user_id)  # 重置状态
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname},,,{mess.level}" + result + "修为，灵石已减半")
            await restart.finish(MessageSegment.image(pic))
        else:
            await restart.finish(f"@{event.sender.nickname},,,{mess.level}" + result + "修为，灵石已减半")

    else : 
        name, root_type = XiuxianJsonDate().linggen_get()
        result = sql_message.ramaker(name, root_type, user_id)

        
        sql_message.update_power2(user_id)  # 更新战力
        sql_message.update_user_hp(user_id)  # 重置状态
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname},{mess.level}" + result)
            await restart.finish(MessageSegment.image(pic))
        else:
            await restart.finish(f"@{event.sender.nickname},{mess.level}" + result)


@command.rank.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """排行榜"""
    await data_check_conf(bot, event)

    message = str(event.message)

    rank_msg = r'[\u4e00-\u9fa5]+'
    message = re.findall(rank_msg, message)
    if message:
        message = message[0]

    if message == "排行榜" or message == "修仙排行榜" or message == "境界排行榜":
        p_rank = sql_message.realm_top()
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + p_rank)
            await rank.finish(MessageSegment.image(pic))
        else:
            await rank.finish(f"@{event.sender.nickname}" + p_rank)
    elif message == "灵石排行榜":
        a_rank = sql_message.stone_top()
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + a_rank)
            await rank.finish(MessageSegment.image(pic))
        else:
            await rank.finish(f"@{event.sender.nickname}" + a_rank)
        
    elif message == "战力排行榜":
        a_rank = sql_message.power_top()
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + a_rank)
            await rank.finish(MessageSegment.image(pic))
        else:
            await rank.finish(f"@{event.sender.nickname}" + a_rank)
    elif message in ["宗门排行榜", "宗门建设度排行榜"]:
        s_rank, _ = sql_message.scale_top()
        pic = await get_msg_pic(s_rank)#
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + s_rank)
            await rank.finish(MessageSegment.image(pic))
        else:
            await rank.finish(f"@{event.sender.nickname}" + s_rank)


# 重置每日签到
@scheduler.scheduled_job(
    "cron",
    hour=0,
    minute=0,
)
async def _():
    sql_message.singh_remake()
    logger.info("每日修仙签到重置成功！")



@command.remaname.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """修改道号"""
    try:
        user_id, group_id, mess = await data_check(bot, event)
    except MsgError:
        return
    except ConfError:
        return

    user_name = args.extract_plain_text().strip()

    len_username = len(user_name.encode('gbk'))
    if len_username > 20:
        msg = "道号长度过长，请修改后重试！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await remaname.finish(MessageSegment.image(pic))
        else:
            await remaname.finish(msg)

    mes = sql_message.update_user_name(user_id, user_name)
    if XiuConfig().img:
        pic = await get_msg_pic(f"@{event.sender.nickname}" + mes)
        await remaname.finish(MessageSegment.image(pic))
    else:
        await remaname.finish(f"@{event.sender.nickname}" + mes)


@command.in_closing.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    """闭关"""
    await data_check_conf(bot, event)
    user_type = 1  # 状态1为闭关
    try:
        user_id, group_id, mess = await data_check(bot, event)
    except MsgError:
        return
    except ConfError:
        return

    user_cd_message = sql_message.get_user_cd(user_id)
    is_type, msg = check_user_type(user_id, 0)
    if is_type:#符合
        sql_message.in_closing(user_id, user_type)
        msg = "进入闭关状态，如需出关，发送【出关】！不要执着于闭关哦小道友，小心走火入魔~"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await in_closing.finish(MessageSegment.image(pic))
        else:
            await in_closing.finish(f"@{event.sender.nickname}" + msg)
    else:
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await in_closing.finish(MessageSegment.image(pic))
        else:
            await in_closing.finish(f"@{event.sender.nickname}" + msg)





async def get_group_id(session_id):
    """获取group_id"""
    res = re.findall("_(.*)_", session_id)
    group_id = res[0]
    return group_id


@command.level_up.handle()
async def update_level(bot: Bot, event: GroupMessageEvent):
    """突破"""
    try:
        user_id, group_id, mess = await data_check(bot, event)
    except MsgError:
        return
    except ConfError:
        return

    if mess.hp is None:
        # 判断用户气血是否为空
        sql_message.update_user_hp(user_id)

    user_msg = sql_message.get_user_message(user_id)  # 用户信息
    user_leveluprate = int(user_msg.level_up_rate)  # 用户失败次数加成

    level_cd = user_msg.level_up_cd
    if level_cd:
        # 校验是否存在CD
        time_now = datetime.now()
        cd = OtherSet().date_diff(time_now, level_cd)  # 获取second
        if cd < XiuConfig().level_up_cd * 60:
            # 如果cd小于配置的cd，返回等待时间
            msg = "目前无法突破，还需要{}分钟".format(XiuConfig().level_up_cd - (cd // 60))
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                await level_up.finish(MessageSegment.image(pic))
            else:
                await level_up.finish(f"@{event.sender.nickname}" + msg)
    else:
        pass

    level_name = user_msg.level  # 用户境界
    exp = user_msg.exp  # 用户修为
    level_rate = jsondata.level_rate_data()[level_name]  # 对应境界突破的概率

    user_backs = sql_message.get_back_msg(user_id) #list(back)
    items = Items()
    pause_flag = False
    if user_backs != None:
        for back in user_backs:
            if int(back.goods_id) == 1999:#检测到有对应丹药
                pause_flag = True
                elixir_name = back.goods_name
                elixir_desc = items.get_data_by_item_id(1999)['desc']
                break
    if pause_flag:
        msg = f"检测到背包有丹药：{elixir_name}，效果：{elixir_desc}请发送 使用、不使用或取消来选择是否使用丹药或取消突破！本次突破概率为：{level_rate + user_leveluprate}%"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await level_up.pause(prompt=MessageSegment.image(pic))
        else:
            await level_up.pause(prompt=f"@{event.sender.nickname}" + msg)
    
    le = OtherSet().get_type(exp, level_rate + user_leveluprate, level_name)

    if le == "失败":
        # 突破失败
        sql_message.updata_level_cd(user_id)  # 更新突破CD

        # 失败惩罚，随机扣减修为
        percentage = random.randint(
            XiuConfig().level_punishment_floor, XiuConfig().level_punishment_limit
        )
        now_exp = int(int(exp) * (percentage / 100))

        sql_message.update_j_exp(user_id, now_exp)  # 更新用户修为
        nowhp = user_msg.hp - (now_exp / 2) if (user_msg.hp - (now_exp / 2)) > 0 else 1
        nowmp = user_msg.mp - now_exp if (user_msg.mp - now_exp) > 0 else 1

        sql_message.update_user_hp_mp(user_id, nowhp, nowmp)  # 修为掉了，血量、真元也要掉

        update_rate = 1 if int(level_rate * XiuConfig().level_up_probability) <= 1 else int(
            level_rate * XiuConfig().level_up_probability)  # 失败增加突破几率

        sql_message.update_levelrate(user_id, user_leveluprate + update_rate)

        msg = "道友突破失败,境界受损,修为减少{}，下次突破成功率增加{}%，失败乃兵家常事，请大侠重新来过！".format(now_exp, update_rate)
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await level_up.finish(MessageSegment.image(pic))
        else:
            await level_up.finish(f"@{event.sender.nickname}" + msg)

    elif type(le) == list:
        # 突破成功
        sql_message.updata_level(user_id, le[0])  # 更新境界
        sql_message.update_power2(user_id)  # 更新战力
        sql_message.restate(user_id)
        sql_message.updata_level_cd(user_id)  # 更新CD
        # sql_message.update_user_attribute(user_id, )
        sql_message.update_levelrate(user_id, 0)
        sql_message.update_user_hp(user_id)  #重置用户HP，mp，atk状态
        msg = "恭喜道友突破{}成功".format(le[0])
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await level_up.finish(MessageSegment.image(pic))
        else:
            await level_up.finish(f"@{event.sender.nickname}" + msg)
    else:
        # 最高境界
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + le)
            await level_up.finish(MessageSegment.image(pic))
        else:
            await level_up.finish(f"@{event.sender.nickname}" + le)

@command.level_up.handle()
async def update_level_end(bot: Bot, event: GroupMessageEvent, mode : str = EventPlainText()):
    await data_check_conf(bot, event)
    isUser, user_info, msg = check_user(event)
    if not isUser:
        await level_up.finish()
    if mode not in ['使用', '不使用', '取消']:
        msg = "指令错误，应该为 使用、不使用或取消！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await level_up.reject(prompt=MessageSegment.image(pic))
        else:
            await level_up.reject(prompt=f"@{event.sender.nickname}" + msg)
    user_id, group_id, user_msg = await data_check(bot, event)

    level_name = user_msg.level  # 用户境界
    exp = user_msg.exp  # 用户修为
    level_rate = jsondata.level_rate_data()[level_name]  # 对应境界突破的概率
    user_leveluprate = int(user_msg.level_up_rate)  # 用户失败次数加成
    
    le = OtherSet().get_type(exp, level_rate + user_leveluprate, level_name)
    user_backs = sql_message.get_back_msg(user_id) #list(back)
    
    items = Items()
    elixir_name = items.get_data_by_item_id(1999)['name']
    if mode == "使用":
        if le == "失败":
            # 突破失败
            sql_message.updata_level_cd(user_id)  # 更新突破CD
            #todu，丹药减少的sql
            sql_message.update_back_j(user_id, 1999, use_key=1)

            update_rate = 1 if int(level_rate * XiuConfig().level_up_probability) <= 1 else int(
                level_rate * XiuConfig().level_up_probability)  # 失败增加突破几率
            sql_message.update_levelrate(user_id, user_leveluprate + update_rate)
            msg = f"道友突破失败，但是使用了丹药{elixir_name}，本次突破失败不扣除修为下次突破成功率增加{update_rate}%，道友不要放弃，切勿颓靡，也莫贪恋美色！"
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                await level_up.finish(MessageSegment.image(pic))
            else:
                await level_up.finish(f"@{event.sender.nickname}" + msg)

        elif type(le) == list:
            # 突破成功
            sql_message.updata_level(user_id, le[0])  # 更新境界
            sql_message.update_power2(user_id)  # 更新战力
            sql_message.updata_level_cd(user_id)  # 更新CD
            # sql_message.update_user_attribute(user_id, )
            sql_message.update_levelrate(user_id, 0)
            sql_message.update_user_hp(user_id)  #重置用户HP，mp，atk状态
            # 丹药减少的sql
            sql_message.update_back_j(user_id, 1999, use_key=1)
            msg = "恭喜道友突破{}成功，祝你仙途美满！".format(le[0])
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                await level_up.finish(MessageSegment.image(pic))
            else:
                await level_up.finish(f"@{event.sender.nickname}" + msg)
        else:
            # 最高境界
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}" + le)
                await level_up.finish(MessageSegment.image(pic))
            else:
                await level_up.finish(f"@{event.sender.nickname}" + le)

    elif mode == "不使用":
        if le == "失败":
            # 突破失败
            sql_message.updata_level_cd(user_id)  # 更新突破CD

            # 失败惩罚，随机扣减修为
            percentage = random.randint(
                XiuConfig().level_punishment_floor, XiuConfig().level_punishment_limit
            )
            now_exp = int(int(exp) * (percentage / 100))

            sql_message.update_j_exp(user_id, now_exp)  # 更新用户修为
            nowhp = user_msg.hp - (now_exp / 2) if (user_msg.hp - (now_exp / 2)) > 0 else 1
            nowmp = user_msg.mp - now_exp if (user_msg.mp - now_exp) > 0 else 1

            sql_message.update_user_hp_mp(user_id, nowhp, nowmp)  # 修为掉了，血量、真元也要掉

            update_rate = 1 if int(level_rate * XiuConfig().level_up_probability) <= 1 else int(
                level_rate * XiuConfig().level_up_probability)  # 失败增加突破几率

            sql_message.update_levelrate(user_id, user_leveluprate + update_rate)

            msg = "道友突破失败,境界受损,修为减少{}，下次突破成功率增加{}%，道友不要放弃，加油特种道友！".format(now_exp, update_rate)
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                await level_up.finish(MessageSegment.image(pic))
            else:
                await level_up.finish(f"@{event.sender.nickname}" + msg)

        elif type(le) == list:
            # 突破成功
            sql_message.updata_level(user_id, le[0])  # 更新境界
            sql_message.update_power2(user_id)  # 更新战力
            sql_message.updata_level_cd(user_id)  # 更新CD
            # sql_message.update_user_attribute(user_id, )
            sql_message.update_levelrate(user_id, 0)
            sql_message.update_user_hp(user_id)  #重置用户HP，mp，atk状态
            msg = "恭喜道友突破{}成功，天助你也！".format(le[0])
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                await level_up.finish(MessageSegment.image(pic))
            else:
                await level_up.finish(f"@{event.sender.nickname}" + msg)
        else:
            # 最高境界
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}" + le)
                await level_up.finish(MessageSegment.image(pic))
            else:
                await level_up.finish(f"@{event.sender.nickname}" + le)

    else:
        msg = "本次突破取消！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await level_up.finish(MessageSegment.image(pic))
        else:
            await level_up.finish(f"@{event.sender.nickname}" + msg)

@command.user_leveluprate.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """我的突破概率"""
    try:
        user_id, group_id, mess = await data_check(bot, event)
    except MsgError:
        return
    except ConfError:
        return
    
    user_msg = sql_message.get_user_message(user_id)  # 用户信息
    leveluprate = int(user_msg.level_up_rate)  # 用户失败次数加成
    
    level_name = user_msg.level  # 用户境界
    level_rate = jsondata.level_rate_data()[level_name]  # 对应境界突破的概率
    # await user_leveluprate.finish(f"道友下一次突破成功概率为{level_rate + leveluprate}%")
    msg = f"道友下一次突破成功概率为{level_rate + leveluprate}%"
    if XiuConfig().img:
        pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
        await user_leveluprate.finish(MessageSegment.image(pic))
    else:
        await user_leveluprate.finish(f"@{event.sender.nickname}" + msg)


@command.give_stone.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """送灵石"""
    try:
        user_id, group_id, mess = await data_check(bot, event)
    except MsgError:
        return
    except ConfError:
        return

    user_message = sql_message.get_user_message(user_id)
    if user_message is None:
        msg = "修仙界没有你的信息！请输入我要修仙，踏入修行"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await give_stone.finish(MessageSegment.image(pic))
        else:
            await give_stone.finish(f"@{event.sender.nickname}" + msg)

    user_stone_num = user_message.stone
    give_qq = None  # 艾特的时候存到这里
    msg = args.extract_plain_text().strip()

    stone_num = re.findall("\d+", msg)  # 灵石数
    nick_name = re.findall("\D+", msg)  # 道号

    if stone_num:
        pass
    else:
        msg = "请输入正确的灵石数量！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await give_stone.finish(MessageSegment.image(pic))
        else:
            await give_stone.finish(f"@{event.sender.nickname}" + msg)

    give_stone_num = stone_num[0]

    if int(give_stone_num) > int(user_stone_num):
        msg = "道友的灵石不够，请重新输入！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await give_stone.finish(MessageSegment.image(pic))
        else:
            await give_stone.finish(f"@{event.sender.nickname}" + msg)

    for arg in args:
        if arg.type == "at":
            give_qq = arg.data.get("qq", "")

    if give_qq:
        if give_qq == user_id:
            msg = "请不要送灵石给自己！"
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                await give_stone.finish(MessageSegment.image(pic))
            else:
                await give_stone.finish(f"@{event.sender.nickname}" + msg)
        else:
            give_user = sql_message.get_user_message(give_qq)
            if give_user:
                sql_message.update_ls(user_id, give_stone_num, 2)  # 减少用户灵石
                give_stone_num2 = int(give_stone_num) * 0.03
                num = int(give_stone_num) - int(give_stone_num2)
                sql_message.update_ls(give_qq, num, 1)  # 增加用户灵石
                msg = "共赠送{}枚灵石给{}道友！收取手续费{}枚".format(
                        give_stone_num, give_user.user_name, int(give_stone_num2)
                    )
                if XiuConfig().img:
                    pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                    await give_stone.finish(MessageSegment.image(pic))
                else:
                    await give_stone.finish(f"@{event.sender.nickname}" + msg)
            else:
                msg = "对方未踏入修仙界，不可赠送！"
                if XiuConfig().img:
                    pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                    await give_stone.finish(MessageSegment.image(pic))
                else:
                    await give_stone.finish(f"@{event.sender.nickname}" + msg)

    if nick_name:
        give_message = sql_message.get_user_message2(nick_name[0])
        if give_message:
            if give_message.user_name == user_message.user_name:
                msg = "请不要送灵石给自己！"
                if XiuConfig().img:
                    pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                    await give_stone.finish(MessageSegment.image(pic))
                else:
                    await give_stone.finish(f"@{event.sender.nickname}" + msg)
            else:
                sql_message.update_ls(user_id, give_stone_num, 2)  # 减少用户灵石
                give_stone_num2 = int(give_stone_num) * 0
                num = int(give_stone_num) 
                sql_message.update_ls(give_message.user_id, num, 1)  # 增加用户灵石
                msg = "共赠送{}枚灵石给{}道友！".format(
                        give_stone_num, give_message.user_name
                    )
                if XiuConfig().img:
                    pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                    await give_stone.finish(MessageSegment.image(pic))
                else:
                    await give_stone.finish(f"@{event.sender.nickname}" + msg)
        else:
            msg = "对方未踏入修仙界，不可赠送！"
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                await give_stone.finish(MessageSegment.image(pic))
            else:
                await give_stone.finish(f"@{event.sender.nickname}" + msg)

    else:
        msg = "未获取道号信息，请输入正确的道号！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await give_stone.finish(MessageSegment.image(pic))
        else:
            await give_stone.finish(f"@{event.sender.nickname}" + msg)

# 传道
@command.chuandao.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """传道，给经验"""
    try:
        user_id, group_id, user_message = await data_check(bot, event)
    except MsgError:
        return
    except ConfError:
        return

    user_message = sql_message.get_user_message(user_id)
    if user_message is None:
        msg = "修仙界没有你的信息！请输入我要修仙，踏入修行"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await give_stone.finish(MessageSegment.image(pic))
        else:
            await give_stone.finish(f"@{event.sender.nickname}" + msg)


    user_jj = jsondata.level_data()[user_message.level]["exp"]
    can_give_exp = user_message.exp - int(user_jj)


    give_qq = None  # 艾特的时候存到这里
    msg = args.extract_plain_text().strip()

    give_exp = re.findall("\d+", msg)  ## 灵石数
    nick_name = re.findall("\D+", msg)  ## 道号

    give_exp_num = give_exp[0]


    # rank1 = sql_message.get_user_message(give_qq)[user_jj] #被传道者的境界
    
    # give_message = sql_message.get_user_message(give_qq)
    # give_user = sql_message.get_user_message(give_qq)
    # give_jj = jsondata.level_data()[give_user.level]["exp"]
    # if give_jj > user_jj:
    #     msg = "对方听说你要给他传道表示不屑一顾！"
    #     if XiuConfig().img:
    #         pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
    #         await chuandao.finish(MessageSegment.image(pic))
    #     else:
    #         await chuandao.finish(f"@{event.sender.nickname}" + msg)
    # else:
    if give_exp_num:
        pass
    else:
        msg = "请输入正确的修为数！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await chuandao.finish(MessageSegment.image(pic))
        else:
            await chuandao.finish(f"@{event.sender.nickname}" + msg)

    if int(give_exp_num) > int(can_give_exp):
        msg = "道友的修为不够，否则将会降境界！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await chuandao.finish(MessageSegment.image(pic))
        else:
            await chuandao.finish(f"@{event.sender.nickname}" + msg)

    for arg in args:
        if arg.type == "at":
            give_qq = arg.data.get("qq", "")

    if give_qq:
        if give_qq == user_id:
            msg = "请不要自己传自己修为！"
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                await chuandao.finish(MessageSegment.image(pic))
            else:
                await chuandao.finish(f"@{event.sender.nickname}" + msg)
        else:
            give_user = sql_message.get_user_message(give_qq)
            give_jj = jsondata.level_data()[give_user.level]["exp"]
            if give_jj > user_jj:
                msg = "对方听说你要给他传道表示不屑一顾！"
                if XiuConfig().img:
                    pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                    await chuandao.finish(MessageSegment.image(pic))
                else:
                    await chuandao.finish(f"@{event.sender.nickname}" + msg)
            else:
                if give_user:
                    sql_message.update_j_exp(user_id,give_exp_num)  # 减少修为
                    num = int(give_exp_num) * 0.5
                    sql_message.update_exp(give_qq, num)  # 增加修为
                    msg = "共传给{}道友{}点修为！传道过程中浪费了一半修为！道友实际获得{}!".format(
                             give_user.user_name,give_exp_num,num,num
                        )
                    if XiuConfig().img:
                        pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                        await chuandao.finish(MessageSegment.image(pic))
                    else:
                        await chuandao.finish(f"@{event.sender.nickname}" + msg)
                else:
                    msg = "对方未踏入修仙界，不可赠送！"
                    if XiuConfig().img:
                        pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                        await chuandao.finish(MessageSegment.image(pic))
                    else:
                        await chuandao.finish(f"@{event.sender.nickname}" + msg)

        # if nick_name:
        #     give_message = sql_message.get_user_message2(nick_name[0])
        #     if give_message:
        #         if give_message.user_name == user_message.user_name:
        #             msg = "请不要传修为给自己！"
        #             if XiuConfig().img:
        #                 pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
        #                 await chuandao.finish(MessageSegment.image(pic))
        #             else:
        #                 await chuandao.finish(f"@{event.sender.nickname}" + msg)
        #         else:
        #             sql_message.update_j_exp(user_id, give_exp_num)  # 减少修为
        #             num = int(give_exp_num) 
        #             sql_message.update_exp(give_message.user_id, num)  # 增加修为
        #             msg = "共传给{}道友{}点修为！".format(
        #                      give_user.user_name,give_exp_num
        #                 )
        #             if XiuConfig().img:
        #                 pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
        #                 await chuandao.finish(MessageSegment.image(pic))
        #             else:
        #                 await chuandao.finish(f"@{event.sender.nickname}" + msg)
        #     else:
        #         msg = "对方未踏入修仙界，不可传道！"
        #         if XiuConfig().img:
        #             pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
        #             await chuandao.finish(MessageSegment.image(pic))
        #         else:
        #             await chuandao.finish(f"@{event.sender.nickname}" + msg)

        # else:
        #     msg = "未获取道号信息，请输入正确的道号！"
        #     if XiuConfig().img:
        #         pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
        #         await chuandao.finish(MessageSegment.image(pic))
        #     else:
        #         await chuandao.finish(f"@{event.sender.nickname}" + msg)

# 偷修为
@command.steal_exp.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    try:
        user_id, group_id, user_message = await data_check(bot, event)
    except MsgError:
        return
    except ConfError:
        return
    
    if cd := check_cd(event, '偷修为'):
        # 如果 CD 还没到 则直接结束
        msg = cd_msg(cd)
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await steal_exp.finish(MessageSegment.image(pic))
        else:
            await steal_exp.finish(f"@{event.sender.nickname}" + msg)

    user_message = sql_message.get_user_message(user_id)
    steal_user = None
    steal_user_exp = None
    steal_qq = None


    for arg in args:
        if arg.type == "at":
            steal_qq = arg.data.get('qq', '')

    if steal_qq:
        if steal_qq == user_id:
            msg = "请不要偷自己刷成就！"
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                await steal_exp.finish(MessageSegment.image(pic))
            else:
                await steal_exp.finish(f"@{event.sender.nickname}" + msg)
        else:
            steal_user = sql_message.get_user_message(steal_qq)
            steal_user_exp = steal_user.exp
            
        steal_user_jj_exp = jsondata.level_data()[steal_user.level]["exp"]
        cost_exp = random.randint(XiuConfig().cost_exp_need_downline,XiuConfig().cost_exp_need_upline)
        can_steal_exp = int(steal_user_exp-steal_user_jj_exp)

        if steal_user:
            steal_success = random.randint(0, 100)
            result = OtherSet().get_power_rate(user_message.power, steal_user.power)
            if isinstance(result, int):
                if int(steal_success) > result:
                    if int(cost_exp) > can_steal_exp:
                        sql_message.update_j_exp(user_id,cost_exp)
                        sql_message.update_exp(steal_qq,cost_exp)
                        add_cd(event,6000,'偷修为')
                        msg = "偷了{}道友修为之后，没偷成，反被{}道友发现，自身修为已经被榨干了，就不要来继续行窃了吧！再偷就掉境界啦！".format(steal_user.user_name,steal_user.user_name)
                        if XiuConfig().img:
                            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                            await steal_exp.finish(MessageSegment.image(pic))
                        else:
                            await steal_exp.finish(f"@{event.sender.nickname}" + msg)
                    sql_message.update_j_exp(user_id,cost_exp)
                    sql_message.update_exp(steal_qq,cost_exp)
                    add_cd(event,6000,'偷修为')
                    msg = "道友偷窃失手了，导致被{}道友发现，损失{}点修为，呜呜呜~".format(steal_user.user_name,cost_exp)
                    if XiuConfig().img:
                        pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                        await steal_exp.finish(MessageSegment.image(pic))
                    else:
                        await steal_exp.finish(f"@{event.sender.nickname}" + msg)


                get_exp_upline = 10000
                get_exp_downline = 5000
                get_exp = random.randint(get_exp_downline,get_exp_upline)
                if int(get_exp) > can_steal_exp:
                    sql_message.update_exp(user_id,can_steal_exp)
                    sql_message.update_j_exp(steal_qq,can_steal_exp)
                    add_cd(event,12000,'偷修为')
                    msg = "偷了{}点修为之后，{}道友的修为已经被榨干了，就不要来找他了吧！再偷就掉境界啦！".format(can_steal_exp,steal_user.user_name)
                    if XiuConfig().img:
                        pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                        await steal_exp.finish(MessageSegment.image(pic))
                    else:
                        await steal_exp.finish(f"@{event.sender.nickname}" + msg)
                else:
                    sql_message.update_exp(user_id,get_exp)
                    sql_message.update_j_exp(steal_qq,get_exp)
                    add_cd(event,12000,'偷修为')
                    msg = "偷到了{}道友{}修为，嘿嘿~开心~yeah~".format(steal_user.user_name,get_exp)
                    if XiuConfig().img:
                        pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                        await steal_exp.finish(MessageSegment.image(pic))
                    else:
                        await steal_exp.finish(f"@{event.sender.nickname}" + msg)
            else:
                msg = result
                if XiuConfig().img:
                    pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                    await steal_exp.finish(MessageSegment.image(pic))
                else:
                    await steal_exp.finish(f"@{event.sender.nickname}" + msg)
        else:
            msg = "对方未踏入修仙界，不要对杂修出手！"
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                await steal_exp.finish(MessageSegment.image(pic))
            else:
                await steal_exp.finish(f"@{event.sender.nickname}" + msg)

# 偷灵石
@command.steal_stone.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    try:
        user_id, group_id, user_message = await data_check(bot, event)
    except MsgError:
        return
    except ConfError:
        return

    if cd := check_cd(event, '偷灵石'):
        # 如果 CD 还没到 则直接结束
        msg = cd_msg(cd)
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await steal_stone.finish(MessageSegment.image(pic))
        else:
            await steal_stone.finish(f"@{event.sender.nickname}" + msg)

    steal_user = None
    steal_user_stone = None

    user_stone_num = user_message.stone
    steal_qq = None  # 艾特的时候存到这里, 要偷的人
    # steal_name = None
    # msg = args.extract_plain_text().strip()

    # nick_name = re.findall("\D+", msg)  ## 道号

    coststone_num = XiuConfig().tou
    if int(coststone_num) > int(user_stone_num):
        msg = '道友的偷窃准备(灵石)不足，请打工之后再切格瓦拉！'
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await steal_stone.finish(MessageSegment.image(pic))
        else:
            await steal_stone.finish(f"@{event.sender.nickname}" + msg)

    for arg in args:
        if arg.type == "at":
            steal_qq = arg.data.get('qq', '')

    if steal_qq:
        if steal_qq == user_id:
            msg = "请不要偷自己刷成就！"
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                await steal_stone.finish(MessageSegment.image(pic))
            else:
                await steal_stone.finish(f"@{event.sender.nickname}" + msg)
        else:
            steal_user = sql_message.get_user_message(steal_qq)
            steal_user_stone = steal_user.stone
    if steal_user:
        steal_success = random.randint(0, 100)
        result = OtherSet().get_power_rate(user_message.power, steal_user.power)
        if isinstance(result, int):
            if int(steal_success) > result:
                sql_message.update_ls(user_id, coststone_num, 2)  # 减少手续费
                sql_message.update_ls(steal_qq, coststone_num, 1)  # 增加被偷的人的灵石
                add_cd(event, XiuConfig().tou_cd, '偷灵石')
                msg = '道友偷窃失手了，被对方发现并被派去华哥厕所义务劳工！赔款{}灵石'.format(coststone_num)
                if XiuConfig().img:
                    pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                    await steal_stone.finish(MessageSegment.image(pic))
                else:
                    await steal_stone.finish(f"@{event.sender.nickname}" + msg)


            get_stone = random.randint(XiuConfig().tou_lower_limit, XiuConfig().tou_upper_limit)

            if int(get_stone) > int(steal_user_stone):
                sql_message.update_ls(user_id, steal_user_stone, 1)  # 增加偷到的灵石
                sql_message.update_ls(steal_qq, steal_user_stone, 2)  # 减少被偷的人的灵石
                add_cd(event, XiuConfig().tou_cd, '偷灵石')
                msg = "{}道友已经被榨干了~".format(steal_user.user_name)
                if XiuConfig().img:
                    pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                    await steal_stone.finish(MessageSegment.image(pic))
                else:
                    await steal_stone.finish(f"@{event.sender.nickname}" + msg)

            else:
                sql_message.update_ls(user_id, get_stone, 1)  # 增加偷到的灵石
                sql_message.update_ls(steal_qq, get_stone, 2)  # 减少被偷的人的灵石
                add_cd(event, XiuConfig().tou_cd, '偷灵石')
                msg = "共偷取{}道友{}枚灵石！".format(steal_user.user_name, get_stone)
                if XiuConfig().img:
                    pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                    await steal_stone.finish(MessageSegment.image(pic))
                else:
                    await steal_stone.finish(f"@{event.sender.nickname}" + msg)

        else:
            msg = result
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                await steal_stone.finish(MessageSegment.image(pic))
            else:
                await steal_stone.finish(f"@{event.sender.nickname}" + msg)

    else:
        msg = "对方未踏入修仙界，不要对杂修出手！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await steal_stone.finish(MessageSegment.image(pic))
        else:
            await steal_stone.finish(f"@{event.sender.nickname}" + msg)


# GM加灵石
@command.gm_command.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    await data_check_conf(bot, event)

    give_qq = None  # 艾特的时候存到这里
    msg = args.extract_plain_text().strip()

    stone_num = re.findall("\d+", msg)  ## 灵石数
    nick_name = re.findall("\D+", msg)  ## 道号

    give_stone_num = stone_num[0]

    if stone_num:
        pass
    else:
        msg = "请输入正确的灵石数量！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await gm_command.finish(MessageSegment.image(pic))
        else:
            await gm_command.finish(f"@{event.sender.nickname}" + msg)

    for arg in args:
        if arg.type == "at":
            give_qq = arg.data.get("qq", "")

    if give_qq:
        give_user = sql_message.get_user_message(give_qq)
        if give_user:
            sql_message.update_ls(give_qq, give_stone_num, 1)  # 增加用户灵石
            msg = "共赠送{}枚灵石给{}道友！".format(give_stone_num, give_user.user_name)
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                await gm_command.finish(MessageSegment.image(pic))
            else:
                await gm_command.finish(f"@{event.sender.nickname}" + msg)
        else:
            msg = "对方未踏入修仙界，不可赠送！"
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                await gm_command.finish(MessageSegment.image(pic))
            else:
                await gm_command.finish(f"@{event.sender.nickname}" + msg)
    elif nick_name:
        give_message = sql_message.get_user_message2(nick_name[0])
        if give_message:
            sql_message.update_ls(give_message.user_id, give_stone_num, 1)  # 增加用户灵石
            msg = "共赠送{}枚灵石给{}道友！".format(give_stone_num, give_message.user_name)
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                await gm_command.finish(MessageSegment.image(pic))
            else:
                await gm_command.finish(f"@{event.sender.nickname}" + msg)
        else:
            msg = "对方未踏入修仙界，不可赠送！"
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                await gm_command.finish(MessageSegment.image(pic))
            else:
                await gm_command.finish(f"@{event.sender.nickname}" + msg)
    else:
        sql_message.update_ls_all(give_stone_num)
        msg = f"全服通告：赠送所有用户{give_stone_num}灵石,请注意查收！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await gm_command.finish(MessageSegment.image(pic))
        else:
            await gm_command.finish(f"@{event.sender.nickname}" + msg)

#GM减灵石
@command.GMMM_command.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    await data_check_conf(bot, event)

    give_qq = None  # 艾特的时候存到这里
    msg = args.extract_plain_text().strip()

    stone_num = re.findall("\d+", msg)  ## 灵石数
    nick_name = re.findall("\D+", msg)  ## 道号

    give_stone_num = stone_num[0]

    if stone_num:
        pass
    else:
        msg = "请输入正确的灵石数量！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await GMMM_command.finish(MessageSegment.image(pic))
        else:
            await GMMM_command.finish(f"@{event.sender.nickname}" + msg)

    for arg in args:
        if arg.type == "at":
            give_qq = arg.data.get("qq", "")

    if give_qq:
        give_user = sql_message.get_user_message(give_qq)
        if give_user:
            sql_message.update_ls(give_qq, give_stone_num, 2)  # 增加用户灵石
            msg = "共减少{}道友{}枚灵石！".format(give_user.user_name,give_stone_num)
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                await GMMM_command.finish(MessageSegment.image(pic))
            else:
                await GMMM_command.finish(f"@{event.sender.nickname}" + msg)
        else:
            msg = "对方未踏入修仙界，不可赠送！"
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                await GMMM_command.finish(MessageSegment.image(pic))
            else:
                await GMMM_command.finish(f"@{event.sender.nickname}" + msg)
    elif nick_name:
        give_message = sql_message.get_user_message2(nick_name[0])
        if give_message:
            sql_message.update_ls(give_message.user_id, give_stone_num, 2)  # 增加用户灵石
            msg = "共减少{}道友{}枚灵石！".format(give_user.user_name,give_stone_num)
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                await GMMM_command.finish(MessageSegment.image(pic))
            else:
                await GMMM_command.finish(f"@{event.sender.nickname}" + msg)
        else:
            msg = "对方未踏入修仙界，不可减少！"
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                await GMMM_command.finish(MessageSegment.image(pic))
            else:
                await GMMM_command.finish(f"@{event.sender.nickname}" + msg)
    else:
        sql_message.update_del_all(give_stone_num)
        msg = f"全服通告：减少所有用户{give_stone_num}灵石,请注意查看！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await GMMM_command.finish(MessageSegment.image(pic))
        else:
            await GMMM_command.finish(f"@{event.sender.nickname}" + msg)

#GM给修为
@command.GGMM_command.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    await data_check_conf(bot, event)
    give_qq = None  # 艾特的时候存到这里
    msg = args.extract_plain_text().strip()

    exp_num = re.findall("\d+", msg)  ## 灵石数
    nick_name = re.findall("\D+", msg)  ## 道号

    give_exp_num = exp_num[0]

    if exp_num:
        pass
    else:
        msg = "请输入正确的灵石数量！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await GGMM_command.finish(MessageSegment.image(pic))
        else:
            await GGMM_command.finish(f"@{event.sender.nickname}" + msg)

    for arg in args:
        if arg.type == "at":
            give_qq = arg.data.get("qq", "")
    
    if give_qq:
        give_user = sql_message.get_user_message(give_qq)
        if give_user:
            sql_message.update_exp(give_qq,give_exp_num)  # 增加用户修为
            msg = "共增加{}道友{}点修为！".format(give_user.user_name,give_exp_num)
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                await GGMM_command.finish(MessageSegment.image(pic))
            else:
                await GGMM_command.finish(f"@{event.sender.nickname}" + msg)
        else:
            msg = "对方未踏入修仙界，不可赠送！"
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                await GGMM_command.finish(MessageSegment.image(pic))
            else:
                await GGMM_command.finish(f"@{event.sender.nickname}" + msg)

    elif nick_name:
        give_message = sql_message.get_user_message2(nick_name[0])
        if give_message:
            sql_message.update_j_exp(give_message.user_id,give_exp_num)  # 增加用户修为
            msg = "共增加{}道友{}点修为！".format(give_message.user_name,give_exp_num)
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                await GGMM_command.finish(MessageSegment.image(pic))
            else:
                await GGMM_command.finish(f"@{event.sender.nickname}" + msg)
        else:
            msg = "对方未踏入修仙界，不可减少！"
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                await GGMM_command.finish(MessageSegment.image(pic))
            else:
                await GGMM_command.finish(f"@{event.sender.nickname}" + msg)
    else:
        sql_message.update_give_allexp(give_exp_num)
        msg = f"全服通告：增加所有用户{give_exp_num}修为,请注意查看！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await GGMM_command.finish(MessageSegment.image(pic))
        else:
            await GGMM_command.finish(f"@{event.sender.nickname}" + msg)



#GM改灵根
@command.gmm_command.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    await data_check_conf(bot, event)
    give_qq = None  # 艾特的时候存到这里
    msg = args.extract_plain_text().strip()

    for arg in args:
        if arg.type == "at":
            give_qq = arg.data.get("qq", "")

    give_user = sql_message.get_user_message(give_qq)
    if give_user:
        sql_message.update_root(give_qq, msg)
        sql_message.update_power2(give_qq)
        msg = "{}道友的修仙境界已变更！".format(give_user.user_name)
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await gmm_command.finish(MessageSegment.image(pic))
        else:
            await gmm_command.finish(f"@{event.sender.nickname}" + msg)
    else:
        msg = "对方未踏入修仙界，不可修改！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await gmm_command.finish(MessageSegment.image(pic))
        else:
            await gmm_command.finish(f"@{event.sender.nickname}" + msg)


@command.rob_stone.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """抢灵石
            player1 = {
            "NAME": player,
            "HP": player,
            "ATK": ATK,
            "COMBO": COMBO
        }"""
    # 验证是否开启抢灵石
    conf = JsonConfig().read_data()
    try:
        if conf['qiang']:
            pass
        else:
            msg = "已关闭抢灵石，请联系管理员！"
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                await rob_stone.finish(MessageSegment.image(pic))
            else:
                await rob_stone.finish(f"@{event.sender.nickname}" + msg)
    except KeyError:
        pass

    try:
        user_id, group_id, user_msg = await data_check(bot, event)
    except MsgError:
        return
    except ConfError:
        return

    if user_msg.hp is None or user_msg.hp == 0:
        # 判断用户气血是否为空
        sql_message.update_user_hp(user_id)

    give_qq = None  # 艾特的时候存到这里
    for arg in args:
        if arg.type == "at":
            give_qq = arg.data.get("qq", "")

    player1 = {"user_id": None, "道号": None, "气血": None, "攻击": None, "真元": None, '会心': None, '防御': 0}
    player2 = {"user_id": None, "道号": None, "气血": None, "攻击": None, "真元": None, '会心': None, '防御': 0}

    if give_qq:
        if give_qq == user_id:
            msg = "请不要偷自己刷成就！"
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                await rob_stone.finish(MessageSegment.image(pic))
            else:
                await rob_stone.finish(f"@{event.sender.nickname}" + msg)

        user_2 = sql_message.get_user_message(give_qq)
        if user_2:
            if user_msg.hp is None or user_msg.hp == 0:
                #判断用户气血是否为None
                sql_message.update_user_hp(user_id)
                user_msg = sql_message.get_user_message(user_id)
            if user_2.hp is None:
                sql_message.update_user_hp(give_qq)
                user_2 = sql_message.get_user_message(give_qq)

            if user_2.hp <= user_2.exp/10:
                msg = "对方重伤藏匿了，无法抢劫！"
                if XiuConfig().img:
                    pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                    await rob_stone.finish(MessageSegment.image(pic))
                else:
                    await rob_stone.finish(f"@{event.sender.nickname}" + msg)

            if user_msg.hp <= user_msg.exp/10:
                msg = "重伤未愈，动弹不得！"
                if XiuConfig().img:
                    pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                    await rob_stone.finish(MessageSegment.image(pic))
                else:
                    await rob_stone.finish(f"@{event.sender.nickname}" + msg)

            player1['user_id'] = user_msg.user_id
            player1['道号'] = user_msg.user_name
            player1['气血'] = user_msg.hp
            player1['攻击'] = user_msg.atk
            player1['真元'] = user_msg.mp
            player1['会心'] = 1

            player2['user_id'] = user_2.user_id
            player2['道号'] = user_2.user_name
            player2['气血'] = user_2.hp
            player2['攻击'] = user_2.atk
            player2['真元'] = user_2.mp
            player2['会心'] = 1


            result, victor = OtherSet().player_fight(player1, player2, 1)
            await send_forward_msg(bot, event, '决斗场', bot.self_id, result)
            if victor == player1['道号']:
                foe_stone = user_2.stone
                if foe_stone > 0:
                    sql_message.update_ls(user_id, int(foe_stone * 0.1), 1)
                    sql_message.update_ls(give_qq, int(foe_stone * 0.1), 2)
                    exps = int(user_2.exp * 0.005)
                    sql_message.update_exp(user_id, exps)
                    sql_message.update_j_exp(give_qq, exps/2)
                    msg = "大战一番，战胜对手，获取灵石{}枚，修为增加{}，对手修为减少{}".format(int(foe_stone*0.1), exps,exps/2)
                    if XiuConfig().img:
                        pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                        await rob_stone.finish(MessageSegment.image(pic))
                    else:
                        await rob_stone.finish(f"@{event.sender.nickname}" + msg)
                else:
                    exps = int(user_2.exp * 0.005)
                    sql_message.update_exp(user_id, exps)
                    sql_message.update_j_exp(give_qq, exps/2)
                    msg = "大战一番，战胜对手，结果对方是个穷光蛋，修为增加{}，对手修为减少{}".format(exps,exps/2)
                    if XiuConfig().img:
                        pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                        await rob_stone.finish(MessageSegment.image(pic))
                    else:
                        await rob_stone.finish(f"@{event.sender.nickname}" + msg)

            elif victor == player2['道号']:
                mind_stone = user_msg.stone
                if mind_stone > 0:
                    sql_message.update_ls(user_id, int(mind_stone * 0.1), 2)
                    sql_message.update_ls(give_qq, int(mind_stone * 0.1), 1)
                    exps = int(user_msg.exp * 0.005)
                    sql_message.update_j_exp(user_id, exps)
                    sql_message.update_exp(give_qq, exps/2)
                    msg = "大战一番，被对手反杀，损失灵石{}枚，修为减少{}，对手获取灵石{}枚，修为增加{}".format(int(mind_stone * 0.1), exps, int(mind_stone * 0.1),exps/2)
                    if XiuConfig().img:
                        pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                        await rob_stone.finish(MessageSegment.image(pic))
                    else:
                        await rob_stone.finish(f"@{event.sender.nickname}" + msg)
                else:
                    exps = int(user_msg.exp * 0.005)
                    sql_message.update_j_exp(user_id, exps)
                    sql_message.update_exp(give_qq, exps/2)
                    msg = "大战一番，被对手反杀，修为减少{}，对手修为增加{}".format(exps,exps/2)
                    if XiuConfig().img:
                        pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                        await rob_stone.finish(MessageSegment.image(pic))
                    else:
                        await rob_stone.finish(f"@{event.sender.nickname}" + msg)

            else:
                msg = "发生错误！"
                if XiuConfig().img:
                    pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                    await rob_stone.finish(MessageSegment.image(pic))
                else:
                    await rob_stone.finish(f"@{event.sender.nickname}" + msg)

        else:
            msg = "没有对方的信息！"
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
                await rob_stone.finish(MessageSegment.image(pic))
            else:
                await rob_stone.finish(f"@{event.sender.nickname}" + msg)




@command.restate.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """重置用户状态。
    单用户：重置状态@xxx
    多用户：重置状态"""


    give_qq = None  # 艾特的时候存到这里
    for arg in args:
        if arg.type == "at":
            give_qq = arg.data.get("qq", "")

    if give_qq:
        sql_message.update_power2(give_qq)  # 更新战力
        sql_message.restate(give_qq)
        msg = '{}用户信息重置成功！'.format(give_qq)
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await restate.finish(MessageSegment.image(pic))
        else:
            await restate.finish(f"@{event.sender.nickname}" + msg)
    else:
        
        sql_message.restate()
        msg = '所有用户信息重置成功！'
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await restate.finish(MessageSegment.image(pic))
        else:
            await restate.finish(f"@{event.sender.nickname}" + msg)


@command.open_robot.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    """抢灵石开关配置"""

    await data_check_conf(bot, event)

    group_msg = str(event.message)
    print(group_msg)

    if "开启" in group_msg:
        JsonConfig().write_data(1)
        msg = "抢灵石开启成功！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await open_robot.finish(MessageSegment.image(pic))
        else:
            await open_robot.finish(f"@{event.sender.nickname}" + msg)

    elif "关闭" in group_msg:
        JsonConfig().write_data(2)
        msg = "抢灵石关闭成功！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await open_robot.finish(MessageSegment.image(pic))
        else:
            await open_robot.finish(f"@{event.sender.nickname}" + msg)

    else:
        msg = "指令错误，请输入：开启抢灵石/关闭抢灵石"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await open_robot.finish(MessageSegment.image(pic))
        else:
            await open_robot.finish(f"@{event.sender.nickname}" + msg)



@command.open_xiuxian.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    """群修仙开关配置"""
    group_msg = str(event.message)
    group_id = await get_group_id(event.get_session_id())

    if "启用" in group_msg:
        JsonConfig().write_data(3, group_id)
        msg = "当前群聊修仙模组已启用！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await open_xiuxian.finish(MessageSegment.image(pic))
        else:
            await open_xiuxian.finish(f"@{event.sender.nickname}" + msg)

    elif "禁用" in group_msg:
        JsonConfig().write_data(4, group_id)
        msg = "当前群聊修仙模组已禁用！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await open_xiuxian.finish(MessageSegment.image(pic))
        else:
            await open_xiuxian.finish(f"@{event.sender.nickname}" + msg)

    else:
        msg = "指令错误!"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname}" + msg)
            await open_xiuxian.finish(MessageSegment.image(pic))
        else:
            await open_xiuxian.finish(f"@{event.sender.nickname}" + msg)


                # 透
@command.fuck.handle()
async def _(bot: Bot, event: GroupMessageEvent, args: Message = CommandArg()):
    try:
        user_id, group_id, user_message = await data_check(bot, event)
    except MsgError:
        return
    except ConfError:
        return

    if cd := check_cd(event, '透'):
        # 如果 CD 还没到 则直接结束
        msg = cd_msg(cd)
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname} " + msg)
            await fuck.finish(MessageSegment.image(pic))
        else:
            await fuck.finish(f"@{event.sender.nickname} " + msg)

    steal_user = None
    steal_user_stone = None

    user_stone_num = user_message.stone
    steal_qq = None  # 艾特的时候存到这里, 要偷的人
    # steal_name = None
    # msg = args.extract_plain_text().strip()

    # nick_name = re.findall("\D+", msg)  ## 道号

    coststone_num = XiuConfig().fuck
    if int(coststone_num) > int(user_stone_num):
        msg = '道友的嫖资(灵石)不足，姑娘们可不会免费给你透！'
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname} " + msg)
            await fuck.finish(MessageSegment.image(pic))
        else:
            await fuck.finish(f"@{event.sender.nickname} " + msg)

    for arg in args:
        if arg.type == "at":
            steal_qq = arg.data.get('qq', '')

    if steal_qq:
        if steal_qq == user_id:
            msg = "请不要透自己刷成就！"
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname} " + msg)
                await fuck.finish(MessageSegment.image(pic))
            else:
                await fuck.finish(f"@{event.sender.nickname} " + msg)
        else:
            steal_user = sql_message.get_user_message(steal_qq)
            steal_user_stone = steal_user.stone
    if steal_user:
        steal_success = random.randint(0, 100)
        result = random.randint(0, 75) # 透人成功率
        if isinstance(result, int):
            if int(steal_success) > result:
                sql_message.update_ls(user_id, coststone_num, 2)  # 减少手续费
                sql_message.update_ls(steal_qq, coststone_num, 1)  # 增加被偷的人的灵石
                add_cd(event, XiuConfig().fuck_cd, '透')
                msg = '道友透人失手了，被对方发现并被公开处刑！赔款{}灵石'.format(coststone_num)
                if XiuConfig().img:
                    pic = await get_msg_pic(f"@{event.sender.nickname} " + msg)
                    await fuck.finish(MessageSegment.image(pic))
                else:
                    await fuck.finish(f"@{event.sender.nickname} " + msg)


            get_stone = random.randint(XiuConfig().fuck_lower_limit, XiuConfig().fuck_upper_limit)

            if int(get_stone) > int(steal_user_stone):
                sql_message.update_ls(user_id, coststone_num, 2)  # 减少手续费
                sql_message.update_ls(steal_qq, coststone_num, 1)  # 增加被偷的人的灵石

                sql_message.update_ls(user_id, steal_user_stone, 1)  # 增加偷到的灵石
                sql_message.update_ls(steal_qq, steal_user_stone, 2)  # 减少被偷的人的灵石

                exps = int(steal_user.exp * 0.001)
                sql_message.update_exp(user_id, exps)
                sql_message.update_j_exp(steal_qq, exps/2)

                
                add_cd(event, XiuConfig().fuck_cd, '透')
                msg = "xbzz心真坏，摸走了道友全部的灵石，还吸走了{}点修为，{}道友已经被榨干了~".format(exps,steal_user.user_name)
                if XiuConfig().img:
                    pic = await get_msg_pic(f"@{event.sender.nickname} " + msg)
                    await fuck.finish(MessageSegment.image(pic))
                else:
                    await fuck.finish(f"@{event.sender.nickname} " + msg)

            else:
                sql_message.update_ls(user_id, coststone_num, 2)  # 减少手续费
                sql_message.update_ls(steal_qq, coststone_num, 1)  # 增加被偷的人的灵石
                sql_message.update_ls(user_id, get_stone, 1)  # 增加偷到的灵石
                sql_message.update_ls(steal_qq, get_stone, 2)  # 减少被偷的人的灵石

                exps = int(steal_user.exp * 0.001)
                sql_message.update_exp(user_id, exps)
                sql_message.update_j_exp(steal_qq, exps/2)

                add_cd(event, XiuConfig().fuck_cd, '透')
                msg = "小手不干净！竟然顺走了一些嫖资。共顺走了{}道友{}枚灵石！吸走了{}点修为".format(steal_user.user_name, get_stone, exps)
                if XiuConfig().img:
                    pic = await get_msg_pic(f"@{event.sender.nickname} " + msg)
                    await fuck.finish(MessageSegment.image(pic))
                else:
                    await fuck.finish(f"@{event.sender.nickname} " + msg)

        else:
            msg = result
            if XiuConfig().img:
                pic = await get_msg_pic(f"@{event.sender.nickname} " + msg)
                await fuck.finish(MessageSegment.image(pic))
            else:
                await fuck.finish(f"@{event.sender.nickname} " + msg)

    else:
        msg = "对方未踏入修仙界，不要对杂修出手！快骗他修仙！"
        if XiuConfig().img:
            pic = await get_msg_pic(f"@{event.sender.nickname} " + msg)
            await fuck.finish(MessageSegment.image(pic))
        else:
            await fuck.finish(f"@{event.sender.nickname} " + msg)

# -----------------------------------------------------------------------------

async def send_forward_msg(
    bot: Bot,
    event: MessageEvent,
    name: str,  # 转发的用户名称
    uin: str,  # qq
    msgs: list  # 转发内容
):
    """合并消息转发"""
    def to_json(msg):
        return {"type": "node", "data": {"name": name, "uin": uin, "content": msg}}

    messages = [to_json(msg) for msg in msgs]
    if isinstance(event, GroupMessageEvent):
        await bot.call_api(
            "send_group_forward_msg", group_id=event.group_id, messages=messages
        )
    else:
        await bot.call_api(
            "send_private_forward_msg", user_id=event.user_id, messages=messages
        )


async def data_check(bot, event):
    """
    判断用户信息是否存在
    """
    user_qq = event.get_user_id()
    group_id = await get_group_id(event.get_session_id())
    msg = sql_message.get_user_message(user_qq)
    conf_data = JsonConfig().read_data()

    try:
        if group_id in conf_data["group"]:
            print('当前存在禁用数据')
            msg = f"本群已关闭修仙模组，请联系管理员开启！"
            pic = await get_msg_pic(msg)#
            await bot.send(event=event, message=MessageSegment.image(pic))
            raise ConfError
        else:
            pass
    except KeyError:
        pass

    if msg:
        pass
    else:
        msg = f"没有您的信息，输入【我要修仙】加入！"
        pic = await get_msg_pic(msg)#
        await bot.send(event=event, message=MessageSegment.image(pic))
        raise MsgError

    return user_qq, group_id, msg


class MsgError(ValueError):
    pass


class ConfError(ValueError):
    pass


@driver.on_shutdown
async def close_db():
    sql_message.close_dbs()
