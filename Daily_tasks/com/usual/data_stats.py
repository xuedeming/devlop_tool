# 试用申请数据统计
import xlwt
import pymysql


class Mysql:
    def __init__(self):
        self.content = pymysql.Connect(
            host='192.168.0.160',
            port=3306,
            user='root',
            passwd='zsyl@db',
            db='pt_edu',
            charset='utf8',
        )
        self.cursor = self.content.cursor(cursor=pymysql.cursors.DictCursor)

    def query(self):
        # 创建工作簿
        wb = xlwt.Workbook(encoding='utf-8')
        # 创建表
        ws = wb.add_sheet('闯关关卡')
        # 行数
        row_num = 0
        font_style = xlwt.XFStyle()
        # 二进制
        font_style.font.bold = True
        # 表头内容
        columns = ['区域', '学校', '职位', '姓名', '电话', '时间', 'IP', '备注']
        # 写进表头内容
        for col_num in range(len(columns)):
            # print(col_num)
            ws.write(row_num, col_num, columns[col_num], font_style)
        # font_style = xlwt.XFStyle()  # 将列名加粗后重新设置

        sql = 'SELECT address,school,position,username,mobile,create_time,apply_ip,remark from try_apply '

        self.cursor.execute(sql)
        for row in self.cursor.fetchall():
            print(row)
            # print(f"一共查找到：{self.cursor.rowcount}")
            # row = ['' if i == 'nan' else i for i in row]  # 如果某项为nan则设置为空

            row_num += 1
            # 逐行写入Excel
        #     for col_num in range(len(row)):
        #         print(col_num)
        #         ws.write(row_num, col_num, row[col_num], font_style)
        #
        # wb.save(r'C:/Users/Admin/Desktop/今日使用申请数据.xls')

        # for row in self.cursor.fetchall():
        #     print(row)

    def end(self):
        self.cursor.close()
        self.content.close()


if __name__ == '__main__':
    m = Mysql()
    m.query()
    m.end()
