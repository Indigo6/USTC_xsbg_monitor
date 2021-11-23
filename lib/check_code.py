import imageio
import cv2 as cv
import numpy as np

from .session import MySession

'''
# extract the digit from check code
imgDat = imageio.imread('checkcode.png') 
for i in range(4):
    dig = imgDat[:, i * 10 : i * 10 + 10, :]
    imageio.imwrite('dig' + str(i) + '.png', dig)
'''


def distance(dat1, dat2):
    d = np.sqrt(dat1[:, :, 0] - dat2[:, :, 0])
    d += np.sqrt(dat1[:, :, 1] - dat2[:, :, 1])
    d += np.sqrt(dat1[:, :, 2] - dat2[:, :, 2])
    return np.sum(d)


def platform_check_code():
    # get the digit from digit_images folder
    digit = []
    for i in range(10):
        img_dat = imageio.imread('digit_imgs/platform/' + str(i) + '.png')
        digit.append(img_dat)

    check_code = ''
    # now start to find the right digit
    img_dat = imageio.imread('check_code.png')
    for i in range(4):
        # get next digit in the image
        data = img_dat[:, i * 10: i * 10 + 10, :]

        # compare to the digit array and find the best match
        min_j = -1
        min_d = 0xffffffff
        for j in range(10):
            d = distance(digit[j], data)
            if d < min_d:
                min_j = j
                min_d = d
        check_code += str(min_j)

    return check_code


def universal_check_code():
    digits = {}
    splits = [28, 48, 68, 88, 108]
    for i in range(10):
        img_dat = cv.imread('digit_imgs/universal/' + str(i) + '.jpg')
        ref = cv.cvtColor(img_dat, cv.COLOR_BGR2GRAY)
        ref = cv.threshold(ref, 200, 255, cv.THRESH_BINARY_INV)[1]
        # ref_contours, hierarchy = cv.findContours(ref.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
        # if i == 2:
        #     ref_contours = ref_contours[:1]
        # ref = ref_contours[0]
        digits[i] = ref

    check_code = ''
    # now start to find the right digit
    img_dat = cv.imread('digit_imgs/universal/check_code.png')
    for i in range(4):
        # get next digit in the image
        data = img_dat[1:-1, splits[i]: splits[i + 1], :]
        data = cv.medianBlur(data, 3)
        ref = cv.cvtColor(data, cv.COLOR_BGR2GRAY)
        ref = cv.threshold(ref, 200, 255, cv.THRESH_BINARY_INV)[1]
        ref = cv.copyMakeBorder(ref, 0, 0, 10, 10, cv.BORDER_CONSTANT, value=[0, 0, 0])
        # cv_show(n, ref)
        # 计算匹配得分: 0得分多少,1得分多少...
        scores = []  # 单次循环中,scores存的是一个数值 匹配 10个模板数值的最大得分

        # 在模板中计算每一个得分
        # digits的digit正好是数值0,1,...,9;digitROI是每个数值的特征表示
        for (digit, digitROI) in digits.items():
            # 进行模板匹配, res是结果矩阵
            res = cv.matchTemplate(ref, digitROI, cv.TM_CCOEFF)  # 此时roi是X digitROI是0 依次是1,2.. 匹配10次,看模板最高得分多少
            max_score = cv.minMaxLoc(res)[1]  # 返回4个,取第二个 最大值 max score
            scores.append(max_score)  # 10个最大值
        check_code += str(np.argmax(scores))  # 返回的是输入列表中最大值的位置
    return check_code


if __name__ == "__main__":
    def cv_show(name, img):  # 自定义的展示函数
        cv.imshow(name, img)
        cv.waitKey(0)
    n = 'text'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/77.0.3865.75 Safari/537.36',
        "Host": "passport.ustc.edu.cn"
    }
    check_code_site = "https://passport.ustc.edu.cn/validatecode.jsp?type=login"
    s = MySession()
    s.headers.update(headers)
    img = s.get(check_code_site).content
    with open('digit_imgs/universal/check_code.png', 'wb') as f:
        f.write(img)
    code = universal_check_code()
    print(code)
    # img = cv.imread('digit_imgs/universal/check_code.png')
    # imgs = [img[:, 27:44], img[:, 48:66], img[:, 68:87], img[:, 88:108]]
    # for i, s_img in enumerate(imgs):
    #     s_img = cv.medianBlur(s_img, (3, 3), 0)
    #     # cv2.imshow('test', s_img)
    #     # cv2.waitKey(0)
    #     cv.imwrite('digit_imgs/universal/s'+str(i)+'.jpg', s_img)
