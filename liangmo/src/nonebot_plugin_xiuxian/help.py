
from .xiuxian_config import XiuConfig

"""
Help帮助信息

"""

__xiuxian_version__ = "v0.4.26"

__xiuxian_notes__ = f"""
指令：
1、我要修仙：进入修仙模式
2、我的修仙信息：获取修仙数据
3、修仙签到：获取灵石及修为
4、重入仙途：重置灵根数据，每次{XiuConfig().remake}灵石
5、传道100@xxx：给指定道友传道，可使用道号
6、改名xx：修改你的道号
7、突破：修为足够后，可突破境界（一定几率失败）
8、闭关、出关、灵石出关：修炼增加修为，挂机功能
9、送灵石100@xxx,偷灵石@xxx,抢灵石@xxx
10、排行榜：修仙排行榜，灵石排行榜，战力排行榜，宗门排行榜
11、悬赏令帮助：获取悬赏令帮助信息
12、我的状态：查看当前HP,我的功法：查看当前技能
13、宗门系统：发送"宗门帮助"获取
14、灵庄系统：发送"灵庄帮助"获取
15、世界BOSS：发送"世界boss帮助"获取
16、功法：发送“我的功法”查看，当前获取途径看“宗门帮助”
17、背包/交友：发送"背包帮助"获取
18、秘境系统：发送"秘境帮助"获取
19、启用/禁用修仙功能：当前群开启或关闭修仙功能
20、炼丹帮助：炼丹功能
21、双修@xxx：与某人共同修炼，一同进步
22、护法@xxx：为他人护法，增加他人突破概率并获得报酬
23、透@xxx：花费灵石获取对方的少量灵石与修为，概率完全随机，与战力无关
23、修仙攻略：其实就是与原版的区别，修仙前请先阅读
""".strip()

# 攻略
__xiuxian_strategy__ = f"""
修仙攻略：
    1、请在江湖好手，练气阶段决定自己的灵根
       筑基后每次洗灵根将会扣除目前的一半修为与灵石：
         1）废灵根：修炼速度50%，战力（攻击）180%
         2）伪灵根：修炼速度60%，战力（攻击）150%
         3）人灵根：修炼速度70%，战力（攻击）130%
         4）地灵根：修炼速度80%，战力（攻击）120%
         5）天灵根：修炼速度110%，战力（攻击）110%
         6）光灵根：修炼速度120%，战力（攻击）130%
         7）暗灵根：修炼速度120%，战力（攻击）130%
    2、神通具有固定属性（金木水火土光暗无），五行相克，光暗互克。
       金克木，木克土，土克水，水克火，火克金  光克暗，暗克光
       满足克制关系时，伤害为正常伤害的1.4倍，被克制时，伤害为正常伤害的0.6倍
       无克制关系时，伤害为正常伤害，无属性神通不受克制，不克制其他属性
       世界BOSS也是有属性的，同样满足上列关系
    3、功法神通可以反复装备（与装备一样无法主动脱下，需要顶替）  
    4、偷修为功能前期代价较大，建议不要轻易尝试，代价与收益均随机，成功后收益为正收益
    5、一定修为后，可以云游，概率获得灵石，修为，功法，神通，装备等
    6、可以与某人双修，花费一定灵石，一同进步
    7、较高进阶或同境界可以为他人护法，增加他人突破概率并获得报酬
    8、透的嫖资（灵石）在成功后也会给予对方作为补偿
    9、灵庄会员提高等级，可以存放更多的灵石，获得更高利息
    10、新增境界大罗境，道祖境，道尊境，道仙境，天道至尊，达到最高境界仍可以闭关但是收益减半
    11、炼丹配方大幅提快，但代价是配方不全，如配方没有请自行计算或将草药出售或找会计算者代练（赚钱之道！）
    *、去偷去抢（bushi
""".strip()