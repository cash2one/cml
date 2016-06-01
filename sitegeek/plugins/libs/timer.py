#!/usr/bin/env python
#-*- coding:utf-8 -*-
import thread
import time

class TimerCounter(object):
    def __init__(self):
        self.thread_local = thread._local()
        self.thread_local.data = {}
        self.thread_local.keys = []

    def trace_begin(self, key):
        node = {"begin": round(1000.0 * time.time(), 2), "end": 0.0}
        if key not in self.thread_local.data:
            self.thread_local.data[key] = [node]
            self.thread_local.keys.append(key)
        else:
            self.thread_local.data[key].append(node)

    def trace_end(self, key):
        if key in self.thread_local.data:
            self.thread_local.data[key][-1]["end"] = round(1000.0 * time.time(), 2)

    def to_string(self, key):
        if key not in self.thread_local.data:
            return ''
        ret = "[ %s : " % key
        total_used = 0.0
        for node in self.thread_local.data[key]:
            time_used = node["end"] - node["begin"]
            if time_used < 0:
                continue
            else:
                ret += "%s|" % round(time_used, 2)
                total_used += time_used
        ret += "(%s) ]\n" % round(total_used, 2)
        return ret

    def to_string_all(self):
        ret = "TimerCounter {\n"
        for key in self.thread_local.keys:
            ret += self.to_string(key)
        ret += "}"
        return ret

    def clear(self):
        self.thread_local.data = {}
        self.thread_local.keys = []

if __name__ == "__main__":
    timer_counter = TimerCounter()
    timer_counter.trace_begin("haha")
    timer_counter.trace_end("haha")
    timer_counter.trace_begin("haha")
    timer_counter.trace_end("haha")
    timer_counter.trace_begin("haha")
    timer_counter.trace_end("haha")
    timer_counter.trace_begin("haha")
    timer_counter.trace_end("haha")

    timer_counter.trace_begin("haha")
    timer_counter.trace_end("haha")
    timer_counter.trace_begin("haha")
    timer_counter.trace_end("haha")
    timer_counter.trace_begin("haha")
    timer_counter.trace_end("haha")

    timer_counter.trace_begin("hah3")
    timer_counter.trace_end("hah3")
    timer_counter.trace_begin("hah3")
    timer_counter.trace_end("hah3")
    timer_counter.trace_begin("hah3")
    timer_counter.trace_end("hah3")

    timer_counter.trace_begin("hah2")
    timer_counter.trace_end("hah2")
    timer_counter.trace_begin("hah2")
    timer_counter.trace_end("hah2")
    timer_counter.trace_begin("hah2")
    timer_counter.trace_end("hah2")
    print timer_counter.to_string_all()
