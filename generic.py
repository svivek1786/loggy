#! /usr/bin/python
import re,sys,os
import loggerRecord,globalS
from time import gmtime, strftime, localtime
logger =  loggerRecord.get_logger()

class generic():
    ''' this class will have generic methods common to both MRA,CMP
    & MPE. Creating a seperate class so that in case of future requirement this
    can be imported and readily used'''

    ############################################################################
    #Function Name  : parseIpfromOutput                                        #
    #Input          : string                                                   #
    #Return Value   : IP's list                                                #
    ############################################################################
    def parseIpfromOutput(self,buf):
        ''' this functions picks out the IP's from buffer string and returns in
        the form of list'''

        ipArr = re.findall("\d+.\d+.\d+.\d+",buf)
        logger.debug("IPs are %s",ipArr)
        return ipArr

    ############################################################################
    #Function Name  : clusterIdIpMap                                           #
    #Input          : string                                                   #
    #Return Value   : IP's list                                                #
    ############################################################################
    def clusterIdIpMap(self,buf):
        '''Remove SIG vip?s add OAM VIP?s
        i.      Parse line by line
        ii.     Take the cluster id & store it in a variable
        iii.    If the cluster id repeats in second line remove the line
        iv.     Similarly form the buffer and pass it to function
        parseIpfromOutput
        '''
        ipArr = []
        clustTmp = ''
        buf = buf.split('\n')
        for line in buf:
            if (re.search('cluster', line)) == None:
                continue
            m = re.match("cluster=(\w+) ipAddr=(\S+)",line)
            if m.group(1) != clustTmp:
                if self.connCheck(m.group(2)):
                    continue
                ipArr.append(m.group(2))
                clustTmp = m.group(1)
        logger.debug("IPs are %s",ipArr)
        return ipArr

    ############################################################################
    #Function Name  : dumpclean                                                #
    #Input          : dict variable                                            #
    #Return Value   : none                                                     #
    ############################################################################
    def dumpclean(obj):
        ''' so far this copied function is not used but placing it for future
        representation of python dictionaries'''

        logger.debug('Python Dictionary Printing start')
        if type(obj) == dict:
            for k, v in obj.items():
                if hasattr(v, '__iter__'):
                    logger.debug('%s',k)
                    dumpclean(v)
                else:
                    logger.debug('%s : %s', (k, v))
        elif type(obj) == list:
            for v in obj:
                if hasattr(v, '__iter__'):
                    dumpclean(v)
                else:
                    logger.debug('%s', v)
        else:
            logger.debug('%s', obj)
        logger.debug('Python Dictionary Printing END')

    ############################################################################
    #Function Name  : dictDumper #
    #Input          :  #
    #Return Value   :  #
    ############################################################################
    def dictDumper(self,obj, nested_level=0, output=sys.stdout):
        ''' recursive function for internal debugging purpose
        source:online'''
        spacing = '   '
        if type(obj) == dict:
            print >> output, '%s{' % ((nested_level) * spacing)
            for k, v in obj.items():
                if hasattr(v, '__iter__'):
                    print >> output, '%s%s:' % ((nested_level + 1) * spacing, k)
                    self.dictDumper(v, nested_level + 1, output)
                else:
                    print >> output, '%s%s: %s' % ((nested_level + 1) * spacing, k, v)
            print >> output, '%s}' % (nested_level * spacing)
        elif type(obj) == list:
            print >> output, '%s[' % ((nested_level) * spacing)
            for v in obj:
                if hasattr(v, '__iter__'):
                    self.dictDumper(v, nested_level + 1, output)
                else:
                    print >> output, '%s%s' % ((nested_level + 1) * spacing, v)
            print >> output, '%s]' % ((nested_level) * spacing)
        else:
            print >> output, '%s%s' % (nested_level * spacing, obj)

    ############################################################################
    #Function Name  : dateTimeFields                                           #
    #Input          : none                                                     #
    #Return Value   : str contains local date & time                           #
    ############################################################################
    def dateTimeFields(self):
        ''' the way how I need the current timestamp which is to be used for file
        names and across all the log files as well'''

        return strftime("%Y%m%d_%H%M%S", localtime())

    ############################################################################
    #Function Name  : dictHexKeyStrip                                          #
    #Input          : python ssh object                                        #
    #Return Value   : str -> hexstring of sshObj python object                 #
    ############################################################################
    def dictHexKeyStrip(self,objDetails):
        ''' take out the hex string and use as unique key for dict database
        as passing this key is much efficient than passing python sshObj'''

        m = re.search('0x[0-9a-fA-F]+',str(objDetails))
        return m.group(0)

    ############################################################################
    #Function Name  : getFileNames                                             #
    #Input          : None                                                     #
    #Return Value   : Dict -> sshObj & log file name mapping                   #
    ############################################################################
    def getFileNames(self):
        ''' function to fetch each file name and its object from the golbal dictionary
        by providing one of it key and store its corresponding value along with its key in new dict
        and return it'''
        fileNameObjDict = {}
        for key1 in globalS.dictDb.keys():
            for key2 in globalS.dictDb[key1].keys():
                if (re.search('FileName', key2)) != None:
                    fileNameObjDict.setdefault(key1,'')
                    fileNameObjDict[key1] += globalS.dictDb[key1].get(key2,'') + ' '
        return fileNameObjDict

    ############################################################################
    #Function Name  : getPids                                                  #
    #Input          : None                                                     #
    #Return Value   : Dict -> sshObj & log file name mapping                   #
    ############################################################################
    def getPids(self):
        '''function to fetch each file name and its object from the golbal dictionary
        by providing one of it key and store its corresponding value along with its key in new dict
        and return it - Not using this as loggy kills all the tail process from the
        system this includes user triggered process as well
        just for simple implementation it is done so should be strict later'''

        fileNameObjDict = {}
        for key1 in globalS.dictDb.keys():
            for key2 in globalS.dictDb[key1].keys():
                if (re.search('PiD', key2)) != None:
                    fileNameObjDict.setdefault(key1,'')
                    fileNameObjDict[key1] += globalS.dictDb[key1].get(key2,'') + ' '
        return fileNameObjDict

    ############################################################################
    #Function Name  : depreceated #
    #Input          :  #
    #Return Value   :  #
    ############################################################################
    def remFilnames(self):
        '''function to remove the file names from the dictionary
        Junk method residing NO more in use - depreceated '''

        fileNameObjDict = {}
        for key1 in globalS.dictDb.keys():
            for key2 in globalS.dictDb[key1].keys():
                if (re.search('FileName', key2, re.I)) != None:
                    fileNameObjDict[globalS.dictDb[key1]['sshObject']] = globalS.dictDb[key1][key2]
        return fileNameObjDict

    ############################################################################
    #Function Name  : chkRedirection                                           #
    #Input          : sshObj -> for which the file name has to checked         #
    #               : typeLog-> type of the Log                                #
    #Return Value   : 1 on redirection enabled, 0 on fileName empty            #
    ############################################################################
    def chkRedirection(self,k,typeLog):
        '''This function check whethetr out dictDataBase contains the file name,
        it stores file name when the redirection takes place'''

        keyFileName =typeLog+'FileName'
        for key2 in globalS.dictDb[k].keys():
            if (re.search(keyFileName, key2, re.I)) != None:
                if globalS.dictDb[k][key2] != '':
                    logger.warn('Already redirection in place further operation prohibited')
                    return 1
                else:
                    logger.warn('fileName key has no value hope redirection is not in place')
                    return 0

    ############################################################################
    #Function Name  : clearRedirection                                         #
    #Input          : k -> unique key which corresponds to each device         #
    #Return Value   : 1 0n failure 0 on success                                #
    ############################################################################
    def clearRedirection(self,k):
        '''once the scp is done please clear the file name from the database so
        that we can execute next set of test case'''
        #if globalS.dictDb[k].get('rcLogPid',0) and globalS.dictDb[k]['rcLogPid'] != '':
        #    logger.warn('Already redirection in place further operation prohibited')
        #    return 1
        #else:
        #    return 0
        fail = 0
        for key2 in globalS.dictDb[k].keys():
            if re.search('FileName', key2, re.I) != None:
                if globalS.dictDb[k][key2] == '':
                    logger.warn('fileName key has no value already! %s', key2)
                    fail += 1
                else:
                    logger.debug('Clearing/re-initialising the filename to none %s', key2)
                    if globalS.dictDb[k].pop(key2, 'Nil') == 'Nil':
                        logger.warn('Database key has no value ! harms')
            if re.search('PiD', key2, re.I) != None:
                if globalS.dictDb[k][key2] == '':
                    logger.warn('PiD key has no value already! hope')
                    fail += 1
                else:
                    logger.debug('Clearing/re-initialising the PiD to none')
                    if globalS.dictDb[k].pop(key2, 'Nil') == 'Nil':
                        logger.warn('Database key has no value ! harms')

        if fail:
            return 1
        else:
            return 0

    ############################################################################
    #Function Name  : getDeviceObjs                                            #
    #Input          : none                                                     #
    #Return Value   : dict with devicetype as key and all its sshObj as value  #
    #                 List for mapping purpose                                 #
    ############################################################################
    def getDeviceObjs(self):
        ''' Function which retrives same product name and returns a new new
        dervied disctionary with key as product/device type & values as list of
        'k' objects '''

        deviceKeyMapDict = {}
        for key1 in globalS.dictDb.keys():
            v = globalS.dictDb[key1]['productName']
            if not v in deviceKeyMapDict:
                deviceKeyMapDict[v] = [key1]
            else:
                deviceKeyMapDict[v].append(key1)
        return deviceKeyMapDict

    ############################################################################
    #Function Name  : formulateFileName                                        #
    #Input          : k-> ssh key Dict                                         #
    #               : sufficFilename-> log file name suffix part               #
    #Return Value   : fileName of the product log                              #
    ############################################################################
    def formulateFileName(self,k,sufficFilename,typeLog):
        ''' Just to have the hostname as filename instead of generic name so that
        this will be helpful in case of multiple MPE's & MRA's differnetiation'''
        fileExtn = '.log'
        if typeLog == 'tcpdump':
            fileExtn = '.pcap'
        logFileName='/tmp/'+globalS.dictDb[k]['hostName']+'_'+typeLog+'_'+sufficFilename+ fileExtn
        logger.info('log fileName is #%s',logFileName)
        return logFileName

    ############################################################################
    #Function Name  : updateDict                                               #
    #Input          : D-> Dict                                                 #
    #               : k1-> primary key                                         #
    #               : k2-> 2ndry key                                           #
    #               : v-> value                                                #
    #Return Value   : 1 0n failure 0 on success                                #
    ############################################################################
    def updateDict(self,d,k1,k2,v):
        ''' a generic function to update global DB with key & value as args. So
        that we can reuse this whwnever we update the global dictionaries'''

        tmpDict={}
        tmpDict[k2]=v
        d[k1].update(tmpDict)
        return 0#always pass

    ############################################################################
    #Function Name  : connCheck                                                #
    #Input          : ipAddress-> ip address of the machine                    #
    #Return Value   : 1 0n failure 0 on success                                #
    ############################################################################
    def connCheck(self,ipAddress):
        ''' issue ping command and check the reachability of the machine. So that
        basic health checkup is administrated before doing ssh'''

        response = os.system("ping -c 1 -w 10 " + ipAddress)
        #and then check the response...
        if response == 0:
          logger.info('hostname# %s is up!',ipAddress)
          return 0
        logger.error('hostname# %s is down!',ipAddress)
        return 1

################################################################################
