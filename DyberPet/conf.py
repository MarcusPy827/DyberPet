import json
import glob
import time
import os.path
from datetime import datetime, timedelta
from sys import platform

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QDesktopWidget
if platform == 'win32':
    basedir = ''
else:
    #from pathlib import Path
    basedir = os.path.dirname(__file__) #Path(os.path.dirname(__file__))
    #basedir = basedir.parent
    basedir = basedir.replace('\\','/')
    basedir = '/'.join(basedir.split('/')[:-1])


class PetConfig:
    """
    宠物配置
    """

    def __init__(self):

        self.petname = None
        self.width = 128
        self.height = 128
        self.scale = 1.0

        self.refresh = 5
        self.interact_speed = 0.02
        self.dropspeed = 1.0
        #self.gravity = 4.0

        self.default = None
        self.up = None
        self.down = None
        self.left = None
        self.right = None
        self.drag = None
        self.fall = None
        self.on_floor = None
        self.patpat = None

        self.subpet = []

        self.random_act = []
        self.act_prob = []
        self.act_name = []
        self.act_type = []
        self.act_sound = []
        self.mouseDecor = {}

        #self.hp_interval = 15
        #self.fv_interval = 15

        self.item_favorite = []
        self.item_dislike = []


    @classmethod
    def init_config(cls, pet_name: str, pic_dict: dict, size_factor):

        path = os.path.join(basedir, 'res/role/{}/pet_conf.json'.format(pet_name))
        with open(path, 'r', encoding='UTF-8') as f:
            o = PetConfig()
            conf_params = json.load(f)

            o.petname = pet_name
            o.scale = conf_params.get('scale', 1.0) * size_factor
            o.width = conf_params.get('width', 128) * o.scale
            o.height = conf_params.get('height', 128) * o.scale

            o.refresh = conf_params.get('refresh', 5)
            o.interact_speed = conf_params.get('interact_speed', 0.02) * 1000
            o.dropspeed = conf_params.get('dropspeed', 1.0)
            #o.gravity = conf_params.get('gravity', 4.0)

            # 
            # 初始化所有动作
            act_path = os.path.join(basedir, 'res/role/{}/act_conf.json'.format(pet_name))
            act_conf = dict(json.load(open(act_path, 'r', encoding='UTF-8')))
            act_dict = {}
            #with open(act_path, 'r', encoding='UTF-8') as f:
            act_dict = {k: Act.init_act(v, pic_dict, o.scale, pet_name) for k, v in act_conf.items()}

            # 载入默认动作
            o.default = act_dict[conf_params['default']]
            o.up = act_dict[conf_params['up']]
            o.down = act_dict[conf_params['down']]
            o.left = act_dict[conf_params['left']]
            o.right = act_dict[conf_params['right']]
            o.drag = act_dict[conf_params['drag']]
            o.fall = act_dict[conf_params['fall']]
            o.prefall = act_dict[conf_params.get('prefall','fall')]
            o.on_floor = act_dict[conf_params['on_floor']]
            o.patpat = act_dict[conf_params.get('patpat', 'default')]

            subpet = conf_params.get('subpet', {})
            for name in subpet:
                subpet[name]['fv_lock'] = subpet[name].get('fv_lock',0)

            o.subpet = subpet

            
            # 初始化随机动作
            random_act = []
            act_prob = []
            act_name = []
            act_type = []
            act_sound = []

            for act_array in conf_params['random_act']:
                random_act.append([act_dict[act] for act in act_array['act_list']])
                act_prob.append(act_array.get('act_prob', 0.2))
                act_name.append(act_array.get('name', None))
                act_type.append(act_array.get('act_type', [2,1]))
                act_sound.append(act_array.get('sound', []))

            o.random_act = random_act
            if sum(act_prob) == 0:
                o.act_prob = [0] * len(act_prob)
            else:
                o.act_prob = [i/sum(act_prob) for i in act_prob]
            o.act_name = act_name
            o.act_type = act_type
            o.act_sound = act_sound


            # 初始化组件动作
            accessory_act = {}
            acc_name = []
            
            for acc_array in conf_params.get("accessory_act", []):
                act_list = [act_dict[act] for act in acc_array['act_list']]
                acc_list = [act_dict[act] for act in acc_array['acc_list']]
                acc_array['act_list'] = act_list
                acc_array['acc_list'] = acc_list
                acc_array['anchor'] = [i*o.scale for i in acc_array['anchor']]
                acc_array['sound'] = acc_array.get('sound', [])

                accessory_act[acc_array['name']] = acc_array
                acc_name.append(acc_array['name'])

            o.accessory_act = accessory_act
            o.acc_name = acc_name

            # 如果是附属宠物 其和主宠物之间的交互
            o.main_interact = conf_params.get("main_interact", {})

            o.item_favorite = conf_params.get('item_favorite', {})
            o.item_dislike = conf_params.get('item_dislike', {})

            # 对话列表
            msg_file = os.path.join(basedir, 'res/role/{}/msg_conf.json'.format(pet_name))
            if os.path.isfile(msg_file):
                msg_data = dict(json.load(open(msg_file, 'r', encoding='UTF-8')))

                msg_dict = conf_params.get("msg_dict", {})
                for msg in msg_dict.keys():
                    msg_dict[msg] = msg_data[msg_dict[msg]]

                o.msg_dict = msg_dict
            else:
                o.msg_dict = {}

            return o


    @classmethod
    def init_sys(cls, pic_dict: dict, size_factor):
        path = os.path.join(basedir, 'res/role/sys/sys_conf.json')
        with open(path, 'r', encoding='UTF-8') as f:
            o = PetConfig()
            conf_params = json.load(f)

            o.petname = 'sys'
            o.scale = conf_params.get('scale', 1.0) * size_factor
            #o.width = conf_params.get('width', 128) * o.scale
            #o.height = conf_params.get('height', 128) * o.scale

            # 
            # 初始化所有动作
            act_path = os.path.join(basedir, 'res/role/sys/act_conf.json')
            act_conf = dict(json.load(open(act_path, 'r', encoding='UTF-8')))
            act_dict = {}
            act_dict = {k: Act.init_act(v, pic_dict, o.scale, 'sys') for k, v in act_conf.items()}
            
            # 初始化随机动作
            '''
            random_act = []
            act_prob = []
            act_name = []
            act_type = []

            for act_array in conf_params['random_act']:
                random_act.append([act_dict[act] for act in act_array['act_list']])
                act_prob.append(act_array.get('act_prob', 0.2))
                act_name.append(act_array.get('name', None))
                act_type.append(act_array.get('act_type', [2,1]))

            o.random_act = random_act
            o.act_prob = [i/sum(act_prob) for i in act_prob]
            o.act_name = act_name
            o.act_type = act_type
            '''

            # 初始化组件动作
            accessory_act = {}
            acc_name = []
            
            for acc_array in conf_params.get("accessory_act", []):
                act_list = [act_dict[act] for act in acc_array['act_list']]
                acc_list = [act_dict[act] for act in acc_array['acc_list']]
                acc_array['act_list'] = act_list
                acc_array['acc_list'] = acc_list
                acc_array['anchor'] = [i*o.scale for i in acc_array['anchor']]
                accessory_act[acc_array['name']] = acc_array
                acc_name.append(acc_array['name'])

            o.accessory_act = accessory_act
            o.acc_name = acc_name

            # 鼠标挂件
            mouseDecor = {}
            for Decor_array in conf_params.get("mouseDecor", []):
                Decor_array['default'] = [act_dict[act] for act in Decor_array['default']]
                Decor_array['click'] = [act_dict[act] for act in Decor_array['click']]
                #Decor_array['anchor'] = [i*o.scale for i in Decor_array['anchor']]
                mouseDecor[Decor_array['name']] = Decor_array

            o.mouseDecor = mouseDecor

            return o


class Act:
    def __init__(self, images=(), act_num=1, need_move=False, direction=None, frame_move=10, frame_refresh=0.04, anchor=[0,0]):
        """
        动作
        :param images: 动作图像
        :param act_num 动作执行次数
        :param need_move: 是否需要移动
        :param direction: 移动方向
        :param frame_move 单帧移动距离
        :param frame_refresh 单帧刷新时间
        """
        self.images = images
        self.act_num = act_num
        self.need_move = need_move
        self.direction = direction
        self.frame_move = frame_move
        self.frame_refresh = frame_refresh
        self.anchor = anchor

    @classmethod
    def init_act(cls, conf_param, pic_dict, scale, pet_name):

        images = conf_param['images']
        img_dir = os.path.join(basedir, 'res/role/{}/action/{}'.format(pet_name, images))
        list_images = glob.glob('{}_*.png'.format(img_dir))
        n_images = len(list_images)
        img = []
        for i in range(n_images):
            img.append(pic_dict["%s_%s"%(images, i)])

        img = [i.scaled(int(i.width() * scale), 
                        int(i.height() * scale),
                        aspectRatioMode=Qt.KeepAspectRatio,
                        transformMode=Qt.SmoothTransformation) for i in img]

        act_num = conf_param.get('act_num', 1)
        need_move = conf_param.get('need_move', False)
        direction = conf_param.get('direction', None)
        frame_move = conf_param.get('frame_move', 10) * scale
        frame_refresh = conf_param.get('frame_refresh', 0.5)
        anchor = conf_param.get('anchor', [0,0])
        return Act(img, act_num, need_move, direction, frame_move, frame_refresh, anchor)


def tran_idx_img(start_idx: int, end_idx: int, pic_dict: dict) -> list:
    """
    转化坐标与图像
    :param start_idx: 开始坐标
    :param end_idx: 结束坐标
    :param pic_dict: 图像dict
    :return: 一个动作所有的图片list
    """
    res = []
    for i in range(start_idx, end_idx + 1):
        res.append(pic_dict[str(i)])
    return res




class PetData:
    """
    宠物数据创建、读取、存储
    """

    def __init__(self):

        #self.petname = pet_name
        self.hp = 100
        self.hp_tier = 3
        self.fv = 0
        self.fv_lvl = 0
        self.items = {}
        self.frozen_data = False

        self.file_path = os.path.join(basedir, 'data/pet_data.json') #%(self.petname)

        self.init_data()

    def init_data(self):

        if os.path.isfile(self.file_path):
            data_params = json.load(open(self.file_path, 'r', encoding='UTF-8'))

            self.hp = data_params['HP']
            self.hp_tier = data_params['HP_tier']
            self.fv = data_params['FV']
            self.fv_lvl = data_params['FV_lvl']
            self.items = data_params['items']

            if 'days' in data_params:
                days = data_params['days']
                now = datetime.now()
                lp = data_params['last_opened'].split('-')
                last_opened = datetime(year=int(lp[0]), month=int(lp[1]), day=int(lp[2]),
                                       hour=now.hour, minute=now.minute, second=now.second)
                if (now - last_opened).days == 0:
                    # 同一天重复打开
                    self.days = days
                    self.last_opened = '%i-%i-%i'%(now.year, now.month, now.day)
                else:
                    self.days = days + 1
                    self.last_opened = '%i-%i-%i'%(now.year, now.month, now.day)


            # 早已使用 但初次统计陪伴时间
            else:
                ct = os.path.getctime(self.file_path)
                ct = time.strptime(time.ctime(ct))
                ct = time.strftime("%Y-%m-%d", ct).split('-')

                now = datetime.now()
                ct = datetime(year=int(ct[0]), month=int(ct[1]), day=int(ct[2]),
                              hour=now.hour, minute=now.minute, second=now.second)
                time_diff = now - ct
                self.days = time_diff.days + 1
                self.last_opened = '%i-%i-%i'%(now.year, now.month, now.day)

        # 初次使用
        else:
            self.hp = -1
            self.hp_tier = 3
            self.fv = 0
            self.fv_lvl = 0
            self.items = {}

            self.days = 1
            now = datetime.now()
            self.last_opened = '%i-%i-%i'%(now.year, now.month, now.day)

        self.save_data()

    def change_hp(self, hp_value, hp_tier=None):
        self.hp = hp_value
        if hp_tier is not None:
            self.hp_tier = int(hp_tier)
        self.save_data()

    def change_fv(self, fv_value, fv_lvl=None):
        self.fv = fv_value
        if fv_lvl is not None:
            self.fv_lvl = fv_lvl
        self.save_data()

    def change_item(self, item, item_change=None, item_num=None):
        if item in self.items.keys():
            if item_change is not None:
                self.items[item] += item_change
            else:
                self.items[item] = item_num
        else:
            if item_change is not None:
                self.items[item] = item_change
            else:
                self.items[item] = item_num
        self.save_data()

    def save_data(self):
        if self.frozen_data:
            return
        #start = time.time()
        data_js = {'HP':self.hp, 'HP_tier':self.hp_tier,
                   'FV':self.fv, 'FV_lvl':self.fv_lvl,
                   'items':self.items,
                   'days':self.days, 'last_opened': self.last_opened}

        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data_js, f, ensure_ascii=False, indent=4)

        #print('Finished in %.2fs'%(time.time()-start))

    def frozen(self):
        self.frozen_data = True




class ItemData:
    """
    物品数据的读取
    """

    def __init__(self):

        self.file_path = os.path.join(basedir, 'res/items/items_config.json')
        self.item_dict = {}
        self.item_conf = dict(json.load(open(self.file_path, 'r', encoding='UTF-8')))
        self.reward_dict = {}
        self.init_data()


    def init_data(self):

        self.item_dict = {k: self.init_item(v) for k, v in self.item_conf.items()}

    def init_item(self, conf_param):
        """
        物品
        :param name: 物品名称
        :param image 物品图片路径
        :param effect_HP: 对饱食度的效果
        :param effect_FV: 对好感度的效果
        :param drop_rate 完成任务后的掉落概率
        :param fv_lock 好感度锁
        :param description 物品描述
        """
        name = conf_param['name']
        image = _load_item_img(conf_param['image'])
        effect_HP = int(conf_param.get('effect_HP', 0))
        
        if effect_HP > 0:
            effect_HP_str = '+%s'%effect_HP
        else:
            effect_HP_str = effect_HP

        effect_FV = int(conf_param.get('effect_FV', 0))
        if effect_FV > 0:
            effect_FV_str = '+%s'%effect_FV
        else:
            effect_FV_str = effect_FV

        drop_rate = float(conf_param.get('drop_rate', 0))
        fv_lock = int(conf_param.get('fv_lock', 1))
        description = self.wrapper(conf_param.get('description', ''))
        item_type = conf_param.get('type', 'consumable')

        if effect_FV==0 and effect_HP==0:
            hint = '{} {}\n{}\n'.format(name,
                                        ' '.join(['★']*fv_lock), 
                                        description)
        else:
            hint = '{} {}\n{}\n_______________\n\n饱食度：{}\n好感度：{}\n'.format(name,
                                                                                  ' '.join(['★']*fv_lock), 
                                                                                  description, 
                                                                                  effect_HP_str, 
                                                                                  effect_FV_str)

        fvs = conf_param.get('fv_reward',[])
        if type(fvs) == int:
            fvs = [fvs]

        if len(fvs) > 0:
            for fv in fvs:
                if fv in self.reward_dict:
                    self.reward_dict[fv].append(name)
                else:
                    self.reward_dict[fv] = []
                    self.reward_dict[fv].append(name)

        pet_limit = conf_param.get('pet_limit', [])
            

        return {'name': name,
                'image': image,
                'effect_HP': effect_HP,
                'effect_FV': effect_FV,
                'drop_rate': drop_rate,
                'fv_lock': fv_lock,
                'hint': hint,
                'item_type': item_type,
                'pet_limit': pet_limit
               }

    def wrapper(self, texts):
        n_char = len(texts)
        n_line = int(n_char//10 + 1)
        texts_wrapped = ''
        for i in range(n_line):
            texts_wrapped += texts[(10*i):min((10*i + 10),n_char)] + '\n'
        texts_wrapped = texts_wrapped.rstrip('\n')

        return texts_wrapped


def _load_item_img(img_path):

    img_file = os.path.join(basedir, 'res/items/{}'.format(img_path))
    return _get_q_img(img_file)

def _get_q_img(img_file) -> QImage:

    image = QImage()
    image.load(img_file)
    return image









