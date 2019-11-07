# 本脚本为批量处理当日培训学校试用申请开通
import pymysql


class Mysql:
    def __init__(self):
        # self.content = pymysql.Connect(
        #     host='xxx-xxx-xxx.xxx.xxx.xxx',
        #     port=xxx,
        #     user='xxx',
        #     passwd='xxx',
        #     db='pt_edu',
        #     charset='utf8',
        # )
        self.content = pymysql.Connect(
            host='xxx.xxx.xxx.xxx',
            port=6,
            user='xxx',
            passwd='xxx',
            db='pt_edu',
            charset='utf8',
        )
        self.cursor = self.content.cursor(cursor=pymysql.cursors.DictCursor)

    def query(self):
        # 查询试用申请数据
        search_try = 'SELECT trp.address,trp.school,trp.username,trp.mobile,' \
                     'DATE_FORMAT( trp.create_time, "%Y-%m-%d")AS create_time,trp.remark ' \
                     'FROM try_apply  trp  where trp.remark = "" and ' \
                     'DATE_FORMAT( trp.create_time, "%Y-%m-%d")=DATE_FORMAT(now(), "%Y-%m-%d") '
        # 添加试用学校
        add_school = 'INSERT INTO `pt_edu`.`com_school`(`name`, `status`,' \
                     ' `test_flag`, `try_status`, `try_end_time`, `province_id`,' \
                     ' `city_id`, `county_id`, `agent_id`, `agent_name`, `remark`, ' \
                     '`create_time`, `forbid_area_codes`) VALUES ' \
                     '( %s, 1, 0, 1, DATE_ADD(now(),INTERVAL 2 month), %s, %s, %s, 1, "中森云数有限公司",' \
                     ' NULL, NOW(), NULL)'
        # 查询试用学校id
        search_school = 'SELECT id from com_school where name = %s'
        # 查询学校名称数量
        scount = 'select count(name)as scount from com_school where name like %s'
        # 修改sys_user表school_id
        modify_school_id = 'UPDATE sys_user set school_id = %s WHERE mobile = %s'
        # 查询用户id
        query_user = 'SELECT id,school_id from sys_user  WHERE mobile= %s'
        # 查询用户其他学校
        query_user_1 = 'SELECT count(id) as ucount from sys_user  WHERE mobile= %s and school_id != 5'
        # 用户新增试用学校老师权限
        add_role = 'INSERT INTO `pt_edu`.`sys_user_role`(`user_id`, `role_flag`, `create_time`, `school_id`) ' \
                   'VALUES (%s, 1,NOW(), %s)'
        # 用户教师角色数量
        user_role = 'select IFNULL(COUNT(sur.user_id),0) as count from sys_user_role sur' \
                    ' where sur.user_id =%s and sur.role_flag = 1'
        # 新增试用学校系列权限
        add_series = 'INSERT INTO `pt_edu`.`com_school_series`( `school_id`, `series_id`, `status`, `desc`, ' \
                     '`create_time`, `dead_line`, `student_nums`) VALUES ( %s, 1, 1, NULL, NOW(), NULL, 500),' \
                     '( %s, 15, 1, NULL, NOW(), NULL, 500),' \
                     '( %s, 16, 1, NULL, NOW(), NULL, 500)'
        # 修改处理状态
        status = 'update try_apply set remark = "已开通" where mobile = %s limit 1'
        status_2 = 'update try_apply set remark = "已开通过，重复数据" where mobile = %s and remark = ""'
        status_3 = 'update try_apply set remark = "未开通，待销售跟进" where mobile = %s and remark = ""'
        # 修改用户名称
        update_name = 'update sys_user set nickname = %s where mobile = %s'
        self.cursor.execute(search_try)
        for row in self.cursor.fetchall():
            address_id = self.get_all_area_id(row["address"])  # 获取学校地区
            print(row["mobile"])
            self.cursor.execute(query_user_1, (row["mobile"]))  # 查询用户其他学校数据
            user_a = self.cursor.fetchall()
            user_count = user_a[0]
            if user_count['ucount'] != 0:
                self.cursor.execute(status_2, (row["mobile"]))
                self.content.commit()
                print('重复数据')
            else:
                self.cursor.execute(query_user, (row["mobile"]))  # 查询用户数据
                id =self.cursor.fetchall()
                if id == ():         # 判断用户是否不存在
                    print('没有此用户')
                    self.cursor.execute(status_3, (row["mobile"]))  # 用户不存在时状态更改
                    self.content.commit()
                    continue;
                user_id= id[0]
                print('用户ID：',user_id["id"],'学校：',row["school"])
                self.cursor.execute(update_name, (row["username"], row["mobile"]))
                self.content.commit()
                self.cursor.execute(user_role, user_id["id"])    # 查询用户教师角色数量
                uesr_r = self.cursor.fetchall()
                user_count = uesr_r[0]
                print('申请用户是否有教师角色：', user_count['count'])
                if user_count['count'] == 0:    # 教师数量判断
                    self.cursor.execute(scount, row["school"])
                    sname = self.cursor.fetchall()
                    sc = sname[0]
                    count = sc['scount']
                    print('学校是否存在：',count)
                    if count == 0:     # 学校是否存在判断
                        self.cursor.execute(add_school, (row["school"], *address_id))
                        self.content.commit()
                    self.cursor.execute(search_school, (row["school"]))
                    school_id = self.cursor.fetchall()
                    for r in school_id:  # 获取学校ID
                        self.cursor.execute(modify_school_id, (r['id'], row["mobile"]))
                        self.cursor.execute(add_role, (user_id["id"], r['id']))
                        if count == 0:
                            self.cursor.execute(add_series, (r['id'], r['id'], r['id']))
                        self.cursor.execute(status, (row["mobile"]))
                        self.content.commit()
                        print("处理成功")
                else:
                    self.cursor.execute(status_2, (row["mobile"]))   # 切换学校后状态为培训学校但已开通试用，更改重复数据状态
                    self.content.commit()
                    print("只修改状态成功")

    def end(self):
        self.cursor.close()
        self.content.close()

    def search_id(self, data):
        search_address_sql = 'SELECT id  from dim_addr WHERE name= %s'
        self.cursor.execute(search_address_sql, data)
        res = self.cursor.fetchone()
        return res["id"]

    def get_all_area_id(self, data: str):
        res = []
        tmp_list = data.split(" ")
        for i in tmp_list:
            res.append(self.search_id(i))
        return res


if __name__ == '__main__':
    m = Mysql()
    m.query()
    m.end()