# -*- coding:utf-8 -*-
# Author : kjy
# Date : 18. 9. 27
# Version : v1.0
# Explanation : 백신 엔진 커널

import os
import StringIO
import datetime
import types
import mmap
import glob

import lmddec
import linvrsa

# class : Engine
# Explanation : 백신 엔진 커널
class Engine:
    # function : __init__(self, debug=False)
    # Explanation : 클래스 초기화
    def __init__(self, debug=False):
        print "Linear Vaccine"
        self.debug = debug
        
        self.modulesPath = None
        self.lmdList = list()
        self.lmdModules = list()

        self.maxDatetime = datetime.datetime(1980, 1, 1, 0, 0, 0, 0)

    # function : setModules(self, modulesPath)
    # Explanation : 인자로 받은 경로에서 암호화된 모듈 리스트를 복호화 하여 암호회 된 모듈을 self.lmdModules에 저장
    # input : modulePath - 모듈 경로
    # return : True - 성공, False - 실패
    def setModules(self, modulesPath):
        self.modulesPath = modulesPath

        pu = linvrsa.read_key(modulesPath + os.sep + 'key.pkr')
        if not pu:
            return False

        ret = self.__getLmdList(modulesPath + os.sep + 'modpriority.lmd', pu)
        if not ret:
            return False

        if self.debug:
            print '[*] modpriority.lmd :'
            print '    ', self.lmdList

        for kmd_name in self.lmdList:
            kmd_path = modulesPath + os.sep + kmd_name
            k = lmddec.LMD(kmd_path, pu)
            module = lmddec.load(kmd_name.split('.')[0], k.body)
            if module:
                self.lmdModules.append(module)
                #print module
                self.__getLastKmdBuildTime(k)

        if self.debug:
            print '[*] lmd_modules :'
            print '    ', self.lmdModules
            print '[*] Last updated %s UTC' % self.maxDatetime.ctime()

        return True

    def __getLastKmdBuildTime(self, lmdInfo):
        d_y, d_m, d_d = lmdInfo.date
        t_h, t_m, t_s = lmdInfo.time
        t_datetime = datetime.datetime(d_y, d_m, d_d, t_h, t_m, t_s)

        if self.maxDatetime < t_datetime:
            self.maxDatetime = t_datetime

    # function : __getLmdList(self, linvLmdListPath, pu)
    # Explanation : 모듈들의 우선순위 파일을 불러옴
    # input : linvLmdListPath - modpriority.lmd 경로, pu - 공개키
    # return : True - 성공, False - 실패
    def __getLmdList(self, linvLmdListPath, pu):
        lmdList = list()

        k = lmddec.LMD(linvLmdListPath, pu)

        if k.body:
            msg = StringIO.StringIO(k.body)

            while True:
                line = msg.readline().strip()

                if not line:
                    break
                elif line.find('.lmd') != -1:
                    lmdList.append(line)
                else:
                    continue

        if len(lmdList):
            self.lmdList = lmdList
            return True
        else:
            return False

    # function : createInstance(self)
    # Explanation : setModules함수에서 저장한 self.lmdModules를 인자로 하여 create함수를 불러 모듈 인스턴스 생성
    # return : ei - 인스턴스, None - 실패
    def createInstance(self):
        ei = EngineInstance(self.modulesPath, self.maxDatetime, self.debug)
        if ei.create(self.lmdModules):
            return ei
        else:
            return None


# class : Engine
# Explanation : 백신 모듈 인스턴스 생성
class EngineInstance:
    # function : __init__(self, modulePath, maxDatetime, debug=False)
    # Explanation : 모듈들의 인스턴스 초기화
    def __init__(self, modulesPath, maxDatetime, debug=False):
        self.debug = debug

        self.modulesPath = modulesPath
        self.maxDatetime = maxDatetime

        self.lvModInst = list()

        self.result = {}
        self.identifiedVirus = set()
    # function : create(self, lmdModules)
    # Explanation : 암호화 된 모듈 인스턴스 생성
    # input : lmdModules - 암호화 된 모듈 이름
    # return : True - 성공, False - 실패
    def create(self, lmdModules):
        for mod in lmdModules:
            try:
                t = mod.LVModule()
                self.lvModInst.append(t)
            except AttributeError:
                continue

        if len(self.lvModInst):
            if self.debug:
                print '[*] Count of Linear Vaccine Modules : %d' % (len(self.lvModInst))
            return True
        else:
            return False

    # function : init(self)
    # Explanation : 모듈 인스턴스들의 init()함수를 실행시켜 초기화 후 tlvModinst 리스트에 넣음
    # return : True - 성공, False - 실패
    def init(self):
        tlvModInst = list()
        if self.debug:
            print '[*] LVModule.init() :'

        for inst in self.lvModInst:
            try:
                ret = inst.init(self.modulesPath)
                if not ret:
                    tlvModInst.append(inst)

                    if self.debug:
                        print '    [-] %s.init() : %d' % (inst.__module__, ret)
            except AttributeError:
                continue

        self.lvModInst = tlvModInst

        if len(self.lvModInst):
            if self.debug:
                print '[*] Count of Linear Vaccine LVModule.init() : %d' % (len(self.lvModInst))

            return True
        else:
            return False

    # function : uninit(self)
    # Explanation : 모듈 인스턴스들의 uninit()함수를 실행시켜 종료
    def uninit(self):
        if self.debug:
            print '[*] LVModule.uninit()'

        for inst in self.lvModInst:
            try:
                ret = inst.uninit()
                if self.debug:
                    print '    [-] %s.uninit() : %d' % (inst.__module__, ret)
            except AttributeError:
                continue

    # function : getInfo(self)
    # Explanation : 모듈 인스턴스에서 getInfo 함수를 실행시켜 모듈 정보를 읽음
    # return : modulesInfo - 모듈들의 정보
    def getInfo(self):
        modulesInfo = list()

        if self.debug:
            print '[*] LVModule.getinfo() :'

        for inst in self.lvModInst:
            try:
                ret = inst.getInfo()
                modulesInfo.append(ret)

                if self.debug:
                    print '    [-] %s.getInfo() :' % inst.__module__
                    for key in ret.keys():
                        print '        - %-10s : %s' % (key, ret[key])
            except AttributeError:
                continue

        return modulesInfo

    # function : scan(self, fileName)
    # Explanation : 입력받은 파일을 모듈별로 검사함
    # input : fileName - 검사할 파일 이름
    # return : result - 악성코드 유무, virusName - 악성코드 이름, virusID - 악성코드 ID, engineID - 검사한 모듈 ID
    def scan(self, fileName, *callback):
        cb_fn = None

        resultValue = {
            'fileName': '',
            'result': False,
            'virusName': '',
            'virusID': -1,
            'moduleID': -1
        }

        try:
            cb_fn = callback[0]
        except IndexError:
            pass

        fileScanList = [fileName]

        while len(fileScanList):
            try:
                realName = fileScanList.pop(0)

                if os.path.isdir(realName):
                    if realName[-1] == os.sep:
                        realName = realName[:-1]

                    resultValue['result'] = False
                    resultValue['fileName'] = realName

                    self.result['Folders'] += 1

                    if isinstance(cb_fn, types.FunctionType):
                        cb_fn(resultValue) # dircallback 넣어줘야 함

                    dirFileList = glob.glob(realName + os.sep + '*')
                    fileScanList = dirFileList + fileScanList

                elif os.path.isfile(realName):
                    result, virusName, virusID, moduleID = self.__scan_file(realName)

                    if result:
                        self.result['InfectedFiles'] += 1
                        self.identifiedVirus.update([virusName])

                    self.result['Files'] += 1

                    resultValue['result'] = result
                    resultValue['virusName'] = virusName
                    resultValue['virusID'] = virusID
                    resultValue['moduleID'] = moduleID
                    resultValue['fileName'] = realName

                    if isinstance(cb_fn, types.FunctionType):
                        cb_fn(resultValue)

            except KeyboardInterrupt:
                return 1

        return 0

    # function : __scan_file(self, fileName)
    # Explanation : 입력받은 파일을 모듈별로 검사함
    # input : fileName - 검사할 파일 이름
    # return : result - 악성코드 유무, virusName - 악성코드 이름, virusID - 악성코드 ID, engineID - 검사한 모듈 ID
    def __scan_file(self, fileName):
        if self.debug:
            print '[*] LVModule.__scan_file() :'
        try:
            result = False
            virusName = str()
            virusID = -1
            moduleID = -1

            fp = open(fileName, 'rb')
            mm = mmap.mmap(fp.fileno(), 0, access=mmap.ACCESS_READ)

            for i, inst in enumerate(self.lvModInst):
                try:
                    result, virusName, virusID = inst.scan(mm, fileName)
                    if result:
                        moduleID = i
                        if self.debug:
                            print '    [-] %s.__scan_file() : %s' % (inst.__module__, virusName)
                        break
                except AttributeError:
                    continue

            if mm:
                mm.close()
            if fp:
                fp.close()

            return result, virusName, virusID, moduleID
        except IOError:
            self.result['IOErrors'] += 1

        return False, '', -1, -1

    # function : disinfect(self, virusName, virusID, engineID)
    # Explanation : 모듈 인스턴스에게 악성코드 치료 요청
    # input : virusName - 악성코드 치료 대상 파일 경로
    #         virusID - 악성코드 ID
    #         engineID - 악성코드를 발견한 모듈 인스턴스 ID
    # return : modulesInfo - 모듈들의 정보
    def disinfect(self, fileName, virusID, engineID):
        ret = False

        if self.debug:
            print '[*] LVModule.disinfect() :'

        try:
            inst = self.lvModInst[engineID]
            ret = inst.disinfect(fileName, virusID)

            if self.debug:
                print '    [-] %s.disinfect() : %s' % (inst.__module__, ret)
        except AttributeError:
            pass

        return ret

    def getVersion(self):
        return self.maxDatetime

    def getSignum(self):
        signum = 0
        for inst in self.lvModInst:
            try:
                info = inst.getInfo()

                if 'sigNum' in info:
                    signum += info['sigNum']

            except AttributeError:
                continue

        return signum

    def setResult(self):
        self.result['Folders'] = 0
        self.result['Files'] = 0
        self.result['Packed'] = 0
        self.result['InfectedFiles'] = 0
        self.result['IdentifiedViruses'] = 0
        self.result['IOErrors'] = 0
        self.result['DisinfectedFiles'] = 0
        self.result['DeletedFiles'] = 0

    def getResult(self):
        self.result['IdentifiedViruses'] = len(self.identifiedVirus)
        return self.result
