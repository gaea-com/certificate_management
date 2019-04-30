# 分页
class Paginator:
    def __init__(self, obj_count=1, obj_perpage=1, pagetag_current=1, pagetag_dsp_count=1):
        '''
        :param obj_count: 获得 条目总数
        :param obj_perpage: 定义 每页显示条目数
        :param pagetag_current: 获得 当前页码
        :param pagetag_dsp_count: 定义 显示多少个页码
        '''
        self.obj_count = obj_count
        self.obj_perpage = obj_perpage

        try:
            pagetag_current = int(pagetag_current)
            if pagetag_current < 1:
                pagetag_current = 1
            self.pagetag_current = pagetag_current
        except Exception as e:
            self.pagetag_current = 1

        self.pagetag_dsp_count = pagetag_dsp_count
        self.pagetag_all_count = self.last_page

    @property
    def obj_slice_start(self):
        return (self.pagetag_current - 1) * self.obj_perpage

    @property
    def obj_slice_end(self):
        return self.pagetag_current * self.obj_perpage

    @property
    def has_prev_page(self):
        return False if self.pagetag_current <= self.first_page else True

    @property
    def has_next_page(self):
        return False if self.pagetag_current >= self.last_page else True

    @property
    def prev_page(self):
        if self.pagetag_current == 1:
            return 1
        elif self.pagetag_current > self.pagetag_all_count:
            return self.pagetag_all_count
        else:
            return self.pagetag_current - 1

    @property
    def next_page(self):
        if self.pagetag_current >= self.pagetag_all_count:
            return self.pagetag_all_count
        else:
            return self.pagetag_current + 1

    @property
    def first_page(self):
        return 1

    @property
    def last_page(self):
        if self.obj_count % self.obj_perpage == 0:
            pagecount = int(self.obj_count / self.obj_perpage)
        else:
            pagecount = int(self.obj_count / self.obj_perpage) + 1
        return pagecount

    @property
    def pagetag_range(self):
        '''页码列表'''
        start = 1
        end = 1
        # pagetag页码数 奇数偶数情况下，前后多少个不同。
        if self.pagetag_dsp_count % 2 == 1:
            before = int(self.pagetag_dsp_count / 2)
            after = before
        else:
            before = int(self.pagetag_dsp_count / 2)
            after = before - 1

        if self.pagetag_all_count < self.pagetag_dsp_count:
            start = 1
            end = self.pagetag_all_count + 1
        elif self.pagetag_current <= before:  # 当前页码过小时
            start = 1
            end = self.pagetag_dsp_count + 1
        elif self.pagetag_current >= self.pagetag_all_count - after:  # 当前页码过大时
            start = self.pagetag_all_count - self.pagetag_dsp_count + 1
            end = self.pagetag_all_count + 1
        else:
            start = self.pagetag_current - before
            end = self.pagetag_current + after + 1
            # print("logging %s %s %s"%(self.pagetag_current,self.pagetag_dsp_count,self.pagetag_dsp_count))

        return range(start, end)
