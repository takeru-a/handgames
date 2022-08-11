import cv2
import numpy as np

class Matchstick():
    def __init__(self) -> None:
        #マッチ棒の数
        N = 22
        #動かせないマッチ棒の指定
        offflags = [3,7,10,15,17]
        #表示するマッチ棒の選択
        init_box = [1] * N
        for n in offflags:
            init_box[n] = 0
        #掴んでいるかどうか
        self.moving = False
        #つまんでいるかどうか
        self.pinch_flag = False
        self.matchstick = init_box 
        self.matchstick_points = [None] * N
        #前の座標
        self.prepoint = None
        
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
        bimg  = cv2.imread('./imgs/matchstick.jpg')
        replay_img  = cv2.imread('./imgs/replay.png')
        # replay_img = cv2.cvtColor(replay_img,cv2.COLOR_BGR2RGB)
        bimg = cv2.resize(bimg, dsize=None, fx=0.2, fy=0.2)
        # bimg = cv2.cvtColor(bimg,cv2.COLOR_BGR2RGB)
        white = np.ones((img.shape), dtype=np.uint8) * 255 #カメラ画像と同じサイズの白画像
        white[0:replay_img.shape[0],img.shape[1]-replay_img.shape[1]:img.shape[1]] = replay_img
        
        #数字の配置
        x = 20
        y = 145
        for i in range(3):
            for j in range(2):
                #マッチ棒の向きの変更
                mimg = np.rot90(bimg,j)
                xd = mimg.shape[1]
                yd = mimg.shape[0]
                #マッチ棒が縦向きの場合  
                #左上から時計回り (0~N) 
                if j == 0:
                    if self.matchstick[i*7] != 0:
                        white[y:yd+y,x:xd+x] = mimg
                    self.matchstick_points[i*7] = [x,y,xd+x,y+yd]
                    x += yd
                    if self.matchstick[i*7+1] != 0:
                        white[y:yd+y,x:xd+x] = mimg
                    self.matchstick_points[i*7+1] = [x,y,xd+x,y+yd]
                    y += yd
                    if self.matchstick[i*7+2] != 0:
                        white[y:yd+y,x:xd+x] = mimg
                    self.matchstick_points[i*7+2] = [x,y,xd+x,y+yd]
                    x -= yd
                    if self.matchstick[i*7+3] != 0:
                        white[y:yd+y,x:xd+x] = mimg
                    self.matchstick_points[i*7+3] = [x,y,xd+x,y+yd]
                    y -= yd
                #マッチ棒が横向きの場合
                #上から順に
                if j==1:
                    if self.matchstick[i*7+4] != 0:
                        white[y:yd+y,x:xd+x] = mimg
                    self.matchstick_points[i*7+4] = [x,y,xd+x,y+yd]
                    y += xd
                    if self.matchstick[i*7+5] != 0: 
                        white[y:yd+y,x:xd+x] = mimg
                    self.matchstick_points[i*7+5] = [x,y,xd+x,y+yd]
                    y += xd
                    if self.matchstick[i*7+6] != 0: 
                        white[y:yd+y,x:xd+x] = mimg
                    self.matchstick_points[i*7+6] = [x,y,xd+x,y+yd]
                    y -= 2*xd
            mimg = bimg
            x += mimg.shape[0] + 135

        #記号の配置
        #固定 (- , =)
        #(-)の配置
        mimg = np.rot90(bimg,1)
        xd = mimg.shape[1]
        yd = mimg.shape[0] 
        x,y = 40+bimg.shape[0], 150+bimg.shape[0]
        white[y:yd+y,x:xd+x] = mimg

        #(=)の配置
        x += x+bimg.shape[0]
        y -= 20
        white[y:yd+y,x:xd+x] = mimg
        y += 40
        white[y:yd+y,x:xd+x] = mimg
        
        #(|)の配置
        mimg = bimg
        xd = mimg.shape[1]
        yd = mimg.shape[0] 
        x, y = 80+bimg.shape[0], 150+(bimg.shape[0]//2)
        if self.matchstick[21] != 0: 
            white[y:yd+y,x:xd+x] = mimg
        self.matchstick_points[21] = [x,y,xd+x,y+yd]
        dwhite = white
        img[dwhite!=[255, 255, 255]] = dwhite[dwhite!=[255, 255, 255]]
 
    
    def pinch(self, img, point):
        #つまんだ座標
        points = [(point[0][0]+point[1][0])//2,(point[0][1]+point[1][1])//2]
        #つまんでいると判断される場合
        if abs(point[0][0]-point[1][0])<=15 and abs(point[0][1]-point[1][1])<=25:
            cv2.circle(img, (points[0], points[1]), 7, (0, 255, 255), 3)
            
            #マッチ棒があるか
            #matchstick_point[x_start,y_start,x_end,y_end]
            for i, matchstick_point in enumerate(self.matchstick_points):
                if self.moving == False and matchstick_point[0] <= points[0] <= matchstick_point[2]:
                    if matchstick_point[1] <= points[1] <= matchstick_point[3]:
                        if self.matchstick[i] != 0:
                            self.matchstick[i] = 0
                            # print(i)
                            self.moving = True
                            self.pinch_flag = True
        #マッチ棒をとり、指を離した場合
        elif self.moving == True:
            for i, matchstick_point in enumerate(self.matchstick_points):
                if matchstick_point[0] <= self.prepoint[0] <= matchstick_point[2]:
                    if matchstick_point[1] <= self.prepoint[1] <= matchstick_point[3]:
                        if self.matchstick[i] != 1:
                            self.matchstick[i] = 1
                            self.moving = False
                            self.pinch_flag = False
        self.prepoint = points    
        return self.pinch_flag
    
    def correct(self):
        flag = False
        correct_box1 = (0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1)
        correct_box2 = (1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0)
        if tuple(self.matchstick) == correct_box1 or tuple(self.matchstick) == correct_box2:
            flag = True
        return flag
    
    def restart(self):
        self.__init__()
        
    def move(self, img, landmarks):
        image_width, image_height = img.shape[1], img.shape[0]
        landmark_point = []
        mimg  = cv2.imread('./imgs/matchstick.jpg')
        mimg = cv2.resize(mimg, dsize=(12,100))
        white = np.ones((img.shape), dtype=np.uint8) * 255

        for _, landmark in enumerate(landmarks.landmark):
            if landmark.visibility < 0 or landmark.presence < 0:
                continue

            # 画面上の座標位置へ変換
            landmark_x = min(int(landmark.x * image_width), image_width - 1)
            landmark_y = min(int(landmark.y * image_height), image_height - 1)
            landmark_z = landmark.z

            landmark_point.append([landmark_x, landmark_y, landmark_z])

        x = mimg.shape[1]//2
        y = mimg.shape[0]//2
        point = [landmark_point[4],landmark_point[8]]
        flag = self.pinch(img,point)
        #つかんでいるマッチ棒の表示
        if flag:
            if landmark_point[8][1] >= y and landmark_point[8][1]<=img.shape[0]-y:
                if landmark_point[8][0] >= x and landmark_point[8][0]<=img.shape[1]-x:
                    white[landmark_point[8][1]-y:landmark_point[8][1]+y,landmark_point[8][0]-x:landmark_point[8][0]+x] = mimg
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