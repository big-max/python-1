#!/usr/bin/env python
# -*- coding:utf-8 -*-
import tornado.ioloop
import tornado.web
import tornado.httpserver
from handler import proj_log
from db import mongoOps
import json
import demjson
import os
import pdb
import re
import pymongo
import time
import uuid
import base64
import datetime
from  proj  import tasks
#配置比对
class compareConfHandler(tornado.web.RequestHandler):
      @tornado.web.asynchronous
      def get(self):
          pass

#这个函数等DB2好了后还要调试
      def createFinalJson(self,ip,product,datetime,instance,db):
          result=mongoOps.db().confCompRunResult.find({'confCompJobRunResult_ip':ip,'confCompJobRunResult_datetime':datetime,'confCompJobRunResult_result':0},{'_id':0})     #首先找出所有的ip 和datetime 在同一个时间点的数据 
          out=[]
          if result:
             for res in result:    # 在找出这个IP和时间点不同的产品和版本
                 retJsonStr=res['confCompJobRunResult_retJson']
                 retJson=json.loads(retJsonStr)
                 if product==retJson['product']:  # 找到一类产品 接着找产品的实例
                    for data in retJson['data']:
                        if db =='-' and data['type'] == 'database' :
                           continue
                        else: 
                           dic={}
                           dic['confCompJobRunResult_ip']=ip
                           dic['confCompJobRunResult_datetime']=datetime
                           dic['confCompJobRunResult_retJson']=data
                           out.append(dic)
          return out

      @tornado.web.asynchronous
      def post(self):
          proj_log.log().info('compareconfHandler: '+self.request.body)
          body=json.loads(self.request.body)
          srcIP=body['srcIP']          
          srcProduct=body['srcProduct']
          srcDatetime=body['srcDatetime']
          srcInstance=body['srcInstance']
          srcDB=body['srcDB']
          targetIP=body['targetIP']          
          targetProduct=body['targetProduct']
          targetDatetime=body['targetDatetime']
          targetInstance=body['targetInstance']
          targetDB=body['targetDB']
          srcOut=self.createFinalJson(srcIP,srcProduct,srcDatetime,srcInstance,srcDB)          
          targetOut=self.createFinalJson(targetIP,targetProduct,targetDatetime,targetInstance,targetDB) 
	  #srcOut.append(targetOut[0])  # 这里targetOut永远只有一个元素 可以用下标0
          for item in targetOut:
              srcOut.append(item)  
     
          final=json.dumps(srcOut)
          proj_log.log().info(final)
          if final:
             self.write({'status':1,'msg':final})
          else:
             self.write({'status':0,'msg':'error'})
          self.finish()

