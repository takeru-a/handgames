import cv2
import numpy as np
import random

class Number():
    def __init__(self) -> None:
        #選択可能タイルの数
        N = 9
        #動かせないタイルの指定
       
        #掴んでいるかどうか
        self.moving = False
        #つまんでいるかどうか
        self.pinch_flag = False
        self.panel_img = self.setup()
        self.panels = [1] * 4 
        rnd = random.randint(0, 3)
        self.panels[rnd] = 0
        self.panel_points = [None] * 4
        #前の座標
        self.prepoint = None
        self.item = 0
        self.item_list = [1] * N
        self.item_points = [None] * N
    
    def ref(self, i):
        j = 0
        if i == 3:
            j = 0
        elif i == 8:
            j = 1
        elif i == 1:
            j = 2
        elif i == 0:
            j = 3
        else:
            j = 4
        return j
     
    def setup(self):
        dataset = self.dataset()
        data = []
        data.append(dataset[3])
        data.append(dataset[8])
        data.append(dataset[1])
        data.append(dataset[0])
        return data
     
     
    def dataset(self):
        dataset = []
        img = cv2.imread('./imgs/2.png')
        dataset.append(img)
        img = cv2.imread('./imgs/3.png')
        dataset.append(img)
        img = cv2.imread('./imgs/5.png')
        dataset.append(img)
        img = cv2.imread('./imgs/6.png')
        dataset.append(img)
        img = cv2.imread('./imgs/7.png')
        dataset.append(img)
        img = cv2.imread('./imgs/8.png')
        dataset.append(img)
        img = cv2.imread('./imgs/mul.png')
        dataset.append(img)
        img = cv2.imread('./imgs/plus.png')
        dataset.append(img)
        img = cv2.imread('./imgs/waru.png')
        dataset.append(img)
        d = []
        for _, img in enumerate(dataset):
            d.append(cv2.resize(img,dsize=(70,70)))
        return d
        
        
    def hand(self, img, landmarks):
        image_width, image_height = img.shape[1], img.shape[0]
        landmark_point = []
        for _, landmark in enumerate(landmarks.landmark):
            if landmark.visibility < 0 or landmark.presence < 0:
                continue

            # 画面上の座標位置へ変換
            landmark_x = min(int(landmark.x * image_width), image_width - 1)
            landmark_y = min(int(landmark.y * image_height), image_height - 1)
            # landmark_z = landmark.z

            landmark_point.append([landmark_x, landmark_y])
        for i in range(len(landmark_point)):
        #サークルを描画
            cv2.circle(img, (landmark_point[i][0], landmark_point[i][1]), 5, (255, 0, 0), -1)
            if i % 4 == 0 and i != 0:
                pass
            elif (i-1) % 4 == 0:
                cv2.line(img, tuple(landmark_point[0]), tuple(landmark_point[i]), (0, 0, 0), 2)
                cv2.line(img, tuple(landmark_point[i]), tuple(landmark_point[i+1]), (0, 0, 0), 2)
            else:
                cv2.line(img, tuple(landmark_point[i]), tuple(landmark_point[i+1]), (0, 0, 0), 2)
    
    def combi(self, img):
        bimg  = cv2.imread('./imgs/eq.png')
        replay_img  = cv2.imread('./imgs/replay.png')
        bimg = cv2.resize(bimg, dsize=(70,70))
        imgs = self.dataset()
        # bimg = cv2.cvtColor(bimg,cv2.COLOR_BGR2RGB)
        white = np.ones((img.shape), dtype=np.uint8) * 255 #カメラ画像と同じサイズの白画像
        white[0:replay_img.shape[0],img.shape[1]-replay_img.shape[1]:img.shape[1]] = replay_img
        #イコール
        #左上
        firstpoint = (150,100)
        x = firstpoint[0] + bimg.shape[1] * 3
        y = firstpoint[1]
        white[y:y+bimg.shape[0],x:x+bimg.shape[1]] = bimg
        cv2.rectangle(img, (x,y), (x+bimg.shape[1], y+bimg.shape[0]), color=(255, 0, 0), thickness=-1)
        # white[0:bimg.shape[0],0:bimg.shape[1]] = bimg
        x = firstpoint[0] 
        y = firstpoint[1] 
        for i, nimg in enumerate(self.panel_img):  
            self.panel_points[i] = [x, y, x+nimg.shape[1], y+nimg.shape[0]]  #panel_points = [x_start, y_start, x_end, y_end]
            cv2.rectangle(img, (x,y), (x+nimg.shape[1], y+nimg.shape[0]), color=(255, 0, 0), thickness=-1)
            if self.panels[i] == 1:
                white[y:y+nimg.shape[0],x:x+nimg.shape[1]] = nimg
            if i == 2: 
                x += nimg.shape[1]*2
            else:
                x += nimg.shape[1]
            
        secondpoint = (150, 300)
        for i, nimg in enumerate(imgs):
            j = i // 5
            y = secondpoint[1] + j*nimg.shape[0]
            k = i % 5
            x = secondpoint[0] + k*nimg.shape[1]
            self.item_points[i] = [x, y, x+nimg.shape[1], y+nimg.shape[0]]  #panel_points = [x_start, y_start, x_end, y_end]
            cv2.rectangle(img, (x,y), (x+nimg.shape[1], y+nimg.shape[0]), color=(0, 255, 0), thickness=2)
            if self.item_list[i] == 1:
                white[y:y+nimg.shape[0],x:x+nimg.shape[1]] = nimg
        
        dwhite = white
        img[dwhite!=[255, 255, 255]] = dwhite[dwhite!=[255, 255, 255]]
 
    
    def pinch(self, img, point):
        #つまんだ座標
        points = [(point[0][0]+point[1][0])//2,(point[0][1]+point[1][1])//2]
        #つまんでいると判断される場合
        if abs(point[0][0]-point[1][0])<=15 and abs(point[0][1]-point[1][1])<=25:
            cv2.circle(img, (points[0], points[1]), 7, (0, 255, 255), 3)
            
            #マッチ棒があるか
            #panel_point[x_start,y_start,x_end,y_end]
            for i, item_point in enumerate(self.item_points):
                if self.moving == False and item_point[0] <= points[0] <= item_point[2]:
                    if item_point[1] <= points[1] <= item_point[3]:
                        if self.item_list[i] != 0:
                            self.item_list[i] = 0
                            self.item = i
                            # print(i)
                            self.moving = True
                            self.pinch_flag = True
        #マッチ棒をとり、指を離した場合
        elif self.moving == True:
            for i, panel_point in enumerate(self.panel_points):
                if panel_point[0] <= self.prepoint[0] <= panel_point[2]:
                    if panel_point[1] <= self.prepoint[1] <= panel_point[3]:
                        if self.panels[i] != 1 and self.ref(self.item) == i:
                            self.panels[i] = 1
                            self.moving = False
                            self.pinch_flag = False
                        else:
                            self.item_list[self.item] = 1
                            self.moving = False
                            self.pinch_flag = False
        self.prepoint = points    
        return self.pinch_flag
    
    def correct(self):
        flag = False
        correct = (1,1,1,1)
        if tuple(self.panels) == correct:
            flag = True
        return flag
    
    def restart(self):
        self.__init__()
        
    def move(self, img, landmarks):
        image_width, image_height = img.shape[1], img.shape[0]
        landmark_point = []
        mimg  = self.dataset()
        white = np.ones((img.shape), dtype=np.uint8) * 255

        for _, landmark in enumerate(landmarks.landmark):
            if landmark.visibility < 0 or landmark.presence < 0:
                continue

            # 画面上の座標位置へ変換
            landmark_x = min(int(landmark.x * image_width), image_width - 1)
            landmark_y = min(int(landmark.y * image_height), image_height - 1)
            landmark_z = landmark.z

            landmark_point.append([landmark_x, landmark_y, landmark_z])

        x = mimg[0].shape[1]//2
        y = mimg[0].shape[0]//2
        point = [landmark_point[4],landmark_point[8]]
        flag = self.pinch(img,point)
        #つかんでいるもの表示
        if flag:
            if landmark_point[8][1] >= y and landmark_point[8][1]<=img.shape[0]-y:
                if landmark_point[8][0] >= x and landmark_point[8][0]<=img.shape[1]-x:
                    white[landmark_point[8][1]-y:landmark_point[8][1]+y,landmark_point[8][0]-x:landmark_point[8][0]+x] = mimg[self.item]
                    dwhite = white
                    img[dwhite!=[255, 255, 255]] = dwhite[dwhite!=[255, 255, 255]]

        #正解に合わせてメッセージを表示
        if self.correct():
            cv2.putText(img, "Great!", (20,60), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,0,0), 2)
        # 64 x 64の画像を使用    
        if landmark_point[8][1] >= 0 and landmark_point[8][1]<=64:
                if landmark_point[8][0] >= img.shape[1]-64 and landmark_point[8][0]<=img.shape[1]:
                    self.restart()
                    cv2.putText(img, "Restart!", (20,60), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255), 2)