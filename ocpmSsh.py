# Embedded file name: /home/satheesh/python_scripts/loggy/build/loggy/out00-PYZ.pyz/ocpmSsh
import pxssh, re, generic, time, sys
import loggerRecord, globalS
logger = loggerRecord.get_logger()
generic = generic.generic()

class ocpmSsh:
    """This class is pure extension of python pexpect module which is wrapped by
    pxssh All remote execution commands oriented methods are written here."""
    sshObjKey = []
    ############################################################################
    #Function Name  : sshServer                                                #
    #Input          : IP -> IP of the machine to connect                       #
    #               : Username & password to connect with                      #
    #Return Value   : python ssh object is returned                            #
    ############################################################################
    def sshServer(self, serverIp, userName, passwd):
        """ setting up SSH connections.
        This logs the user into the given server"""
        logger.debug('Invoked by - %s', __name__)
        self.s = pxssh.pxssh(maxread=2000000, timeout=60)
        fout = file('/tmp/sshTermLogFile.txt', 'a')
        self.s.logfile = fout
        if not self.s.login(serverIp, userName, passwd, auto_prompt_reset=False, login_timeout=60):
            logger.error('SSH session failed on login')
            logger.info('%s', 'str(s)')
        else:
            k = generic.dictHexKeyStrip(self.s)
            logger.info('SSH session login successful, ssh object is # %s', k)
            globalS.dictDb[k] = {'sshObject': self.s}
            self.s.PROMPT = '\\[\\S+\\s~\\]#|$ |password: '
            self.sshObjKey.append(k)
            self.setSudo(k)
            self.getProdName(k)
        return self.s

    ############################################################################
    #Function Name  : exeCmd                                                   #
    #Input          : k--> ssh key                                             #
    #               : cmd --> cmd to send to the terminal                      #
    #Return Value   : string -->output content before the prompt               #
    ############################################################################
    def exeCmd(self, k, cmd):
        """ This sends a string to the child process. This returns the number of
        bytes written. If a log file was set then the data is also written
        to the log"""
        logger.debug('cmd to be triggerd is# %s', cmd)
        sshObj = globalS.dictDb[k]['sshObject']
        sshObj.buffer = ''
        sshObj.sendline(cmd)
        if sshObj.prompt():
            logger.info('Executed cmd # %s', sshObj.before)
            return sshObj.before.strip()
        else:
            logger.error('prompt mismatch error')
            return 0

    ############################################################################
    #Function Name  : setSudo                                                  #
    #Input          : k-> python ssh key                                       #
    #               : cmd -> optional                                          #
    #Return Value   : 0 always                                                 #
    ############################################################################
    def setSudo(self, k, cmd = 'sudo -s'):
        """verify sudo -s is executed and no error is obtanined & prompt is return
        we dont verify  add it later , as in Tekelec we dont get root permission
        on login"""
        self.exeCmd(k, cmd)
        return 0

    ############################################################################
    #Function Name  : getProdName                                              #
    #Input          : k-> ssh Key                                              #
    #               : cmd -> optional                                          #
    #Return Value   : Type of product ie MPE,MRA,CMP etc.,                     #
    ############################################################################
    def getProdName(self, k, cmd = 'getPolicyRev -p'):
        """ to figure out whether its CMP MRA MPE
        issue getPolicyRev to do so or from prompt cross verify & store it
        in our DB for future reference"""
        sshObj = globalS.dictDb[k]['sshObject']
        buf = self.exeCmd(k, cmd)
        if re.search('cmp', buf, re.M | re.I) != None:
            prodName = 'CMP'
        elif re.search('mra', buf, re.M | re.I) != None:
            prodName = 'MRA'
        elif re.search('MPE', buf, re.M | re.I) != None:
            prodName = 'MPE'
        logger.info('server I logged in is # %s', prodName)
        generic.updateDict(globalS.dictDb, k, 'productName', prodName)
        buf = self.exeCmd(k, 'hostname -s')
        buf = buf.split('\n')[1].strip()
        generic.updateDict(globalS.dictDb, k, 'hostName', buf)
        return prodName

    ############################################################################
    #Function Name  : putProdVersion                                           #
    #Input          : k-> ssh Key                                              #
    #                 external Log file Name                                   #
    #Return Value   : s/w revision string                                      #
    ############################################################################
    def putProdVersion(self, k, prodLogFile):
        """This method prints the software version & Ifconfig IP address to the
        log file so that we doesn't loose the information on which build the log
        is taken"""
        logger.debug('save few build infos')
        cmdsList = ['appRev -a', 'hostname -I', 'echo ' + '_' * 80]
        for cmd in cmdsList:
            cmd = cmd + '>>' + prodLogFile
            self.exeCmd(k, cmd)

    ############################################################################
    #Function Name  : redirectMraLog (depreceated)                             #
    #Input          : k -> unique key which corresponds to each device         #
    #                 logFilename -> name of the log file                      #
    #Return Value   : pid -> process id of the tail cmd                        #
    ############################################################################
    def redirectMraLog(self, k, logFilename):
        """ to figure out whether its CMP MRA MPE
        issue getPolicyRev to do so or from prompt cross verify"""
        generic.updateDict(globalS.dictDb, k, 'MraLogFileName', logFilename)
        self.putProdVersion(k, globalS.dictDb[k]['MraLogFileName'])
        logfile = '/var/camiant/log/mra.log'
        cmd = 'tail -f ' + logfile + ' >> ' + globalS.dictDb[k]['MraLogFileName'] + '&2>&1'
        pid = self.exeCmd(k, cmd)
        pid = re.findall(' \\d+', pid)
        generic.updateDict(globalS.dictDb, k, 'mraLogPid', pid)
        logger.info('redirecting mra log to %s with pid#%s', globalS.dictDb[k]['MraLogFileName'], pid)
        return pid

    ############################################################################
    #Function Name  : redirectQPLog                                           #
    #Input          : k -> unique key which corresponds to each device         #
    #                 logFilename -> name of the log file                      #
    #Return Value   : pid -> process id of the tail cmd                        #
    ############################################################################
    def redirectQPLog(self, k, logFilename, typeLog):
        """ to figure out whether its CMP MRA MPE
        issue getPolicyRev to do so or from prompt cross verify"""
        keyFileName = typeLog + 'FileName'
        keyPidName = typeLog + 'PiD'
        cmd = ''
        if typeLog is 'qpLog':
            prodNam = globalS.dictDb[k]['productName']
            logger.info('from method redirectLog for product#%s', prodNam)
            if prodNam is 'MRA':
                logfile = '/var/camiant/log/mra.log'
            elif prodNam is 'MPE':
                logfile = '/var/camiant/log/rc.log'
            cmd = 'tail -f ' + logfile
        elif typeLog is 'qpTrace':
            cmd = 'iqt -E -R1 -T1 qptrace'
        elif typeLog is 'tcpdump':
            prodNam = globalS.dictDb[k]['productName']
            logger.info('from method redirectLog for product#%s', prodNam)
            cmd = 'tcpdump tcp port 3868 and not arp and not udp -w '
        generic.updateDict(globalS.dictDb, k, keyFileName, logFilename)
        if typeLog is 'tcpdump':
            cmdPart = ''
        else:
            self.putProdVersion(k, globalS.dictDb[k][keyFileName])
            cmdPart = ' >> '
        cmd += cmdPart + globalS.dictDb[k][keyFileName] + '&2>&1'
        self.exeCmd(k, cmd)
        pid = self.exeCmd(k, 'echo $!')
        try:
            pid = re.findall('(\\d\\d+)', pid)[0]
        except:
            logger.error('Unexpected error:%s', sys.exc_info()[0])

        generic.updateDict(globalS.dictDb, k, keyPidName, pid)
        logger.debug('redirecting rc log to %s with pid#%s', globalS.dictDb[k][keyFileName], pid)
        return pid

    ############################################################################
    #Function Name  : redirectLog                                              #
    #Input          : k -> python ssh handle                                   #
    #               : sufficFilename-> log file name suffix part               #
    #Return Value   : process id                                               #
    ############################################################################
    def redirectLog(self, k, sufficFilename, typeLog):
        """ generic function to redirect the logs
        which inturn calls two methods"""
        if generic.chkRedirection(k, typeLog):
            return 'void'
        fileNam = generic.formulateFileName(k, sufficFilename, typeLog)
        logger.debug('redirecting log type# %s', typeLog)
        pid = self.redirectQPLog(k, fileNam, typeLog)
        return pid

    ############################################################################
    #Function Name  : addrProdCorr                                             #
    #Input          : sshObj -> cmp ssh object                                 #
    #Return Value   : SQL Table as string                                      #
    ############################################################################
    def addrProdCorr(self, sshObj):
        """ ip address & product name correlation takes here. We use the database
        of CMP to knw its associated MRA's & MPE's. The main hint is it gives us
        signaling IP's So loggy tool has a precondition of working over signalling
        IP's not over OAM signaling VIP's. So Kindly ensure SIG VIP's are configure
        properly"""
        k = generic.dictHexKeyStrip(sshObj)
        bufTable = self.exeCmd(k, 'iqt -E HaVipDef')
        ipAddList = generic.clusterIdIpMap(bufTable)
        return ipAddList

    def __del__(self):
        """ basicall call methods like closing the ssh connection exiting the
        sql etc while python cleanup. In case if python encounters KILLSIG this
        method gets invoked and gracefully closes the ssh connection"""
        self.sshClose()

    ############################################################################
    #Function Name  : sshClose                                                 #
    #Input          : None                                                     #
    #Return Value   : None                                                     #
    ############################################################################
    def sshClose(self):
        """ basicall call methods like closing the ssh connection exiting the
        sql etc while python cleanup kill the tail process that we started at
        back ground etc """
        logger.debug('Procees to be killed')
        self.pidsKill()
        for key in self.sshObjKey:
            obj = globalS.dictDb[key]['sshObject']
            logger.info('gonna close the object at # %s', key)
            obj.close()

        loggerRecord.shutdown()

    ############################################################################
    #Function Name  : scpFiles                                                 #
    #Input          : IP -> machine where the log files to be stored           #
    #               : Username & password for authentication                   #
    #               : path -> please ensure this path is available in remote   #
    #                 server                                                   #
    #Return Value   : 1 0n failure 0 on success                                #
    ############################################################################
    def scpFiles(self, serverIp, userName, passwd, path):
        """ a propritery method to do SCP as we cant do SCP from running machine
        we need to login to the machine where the file is. Here the main
        enchancement if path is not defined put the logs to some default folder
        else print and also mechanism to figure it whether its success or not"""
        fileNameObjDict = {}
        fileNameObjDict = generic.getFileNames()
        if len(fileNameObjDict) == 0:
            logger.warn('No files available to scp ! kindly redirect them first')
        self.pidsKill()
        for k, v in fileNameObjDict.items():
            if generic.clearRedirection(k):
                continue
            cmd = 'chmod o+r ' + v
            self.exeCmd(k, cmd)
            cmd = 'scp -p -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no ' + v + ' root@' + serverIp + ':' + path
            self.exeCmd(k, cmd)
            time.sleep(15)
            self.exeCmd(k, passwd)
            self.exeCmd(k, '\n')

        return 0

    ############################################################################
    #Function Name  : dictDumper                                               #
    #Input          : None                                                     #
    #Return Value   : prints all the main dictionary for debugging purpose only#
    ############################################################################
    def dictDumper(self):
        """ strictly for internal debugging purpose should not be called explicity
        as print to stdout is used """
        print 'globalS.dictDb Dictionary Printing start '
        generic.dictDumper(globalS.dictDb)
        print 'dictDb Dictionary Printing END'
        fileNameObjDict = generic.getPids()
        print 'fileNameObjDict Dictionary Printing start'
        generic.dictDumper(fileNameObjDict)
        print 'fileNameObjDict Dictionary Printing END'
        pidObjDict = generic.getFileNames()
        print 'pidObjDict Dictionary Printing start'
        generic.dictDumper(pidObjDict)
        print 'pidObjDict Dictionary Printing END'
        deviceKeyMapDict = generic.getDeviceObjs()
        print 'deviceKeyMapDict Dictionary Printing start '
        generic.dictDumper(deviceKeyMapDict)
        print 'deviceKeyMapDict Dictionary Printing END'
        return 0

    ############################################################################
    #Function Name  : detectMulDevRedirect                                     #
    #Input          : None                                                     #
    #Return Value   : prints all the main dictionary for debugging purpose only#
    ############################################################################
    def detectMulDevRedirect(self, prodName, sufFileName, typeLog):
        """ detect multiple active device so that we can ask user which 1 to
        redirect of both by default"""
        devKeyMapDict = generic.getDeviceObjs()
        tmpKList = devKeyMapDict[prodName]
        if len(tmpKList) > 1:
            logger.info('Multiple %s is found be default will log both device', prodName)
        for k in tmpKList:
            logger.debug('redirect log of %s', globalS.dictDb[k]['hostName'])
            self.redirectLog(k, sufFileName, typeLog)

        return 0

    ############################################################################
    #Function Name  : pidsKill                                               #
    #Input          : None                                                     #
    #Return Value   : prints all the main dictionary for debugging purpose only#
    ############################################################################
    def pidsKill(self):
        """ strictly for internal debugging purpose should not be called explicity
        as print to stdout is used Kills all the redirected files process by
        sending SIGINT"""
        pidObjDict = {}
        pidObjDict = generic.getPids()
        for k, v in pidObjDict.items():
            v = v.strip()
            if v != '':
                cmd = 'kill -SIGINT ' + v
                self.exeCmd(k, cmd)

        return 0

    def setPrompt(self):
        """this method sets the prompt of pexpect and can be reverted to any prompt
        """
        pidObjDict = {}
        pidObjDict = generic.getPids()
        for k, v in pidObjDict.items():
            v = v.strip()
            if v != '':
                cmd = 'kill -SIGINT ' + v
                self.exeCmd(k, cmd)

        return 0

    def reinitialisation(self):
        """ When user is not sure about the steps or have to restart the
        redirection this function is called"""
        fail = 0
        fileNameObjDict = {}
        fileNameObjDict = generic.getFileNames()
        if len(fileNameObjDict) == 0:
            logger.warn('No files are redirected so far ! kindly redirect them first')
        self.pidsKill()
        for k in fileNameObjDict.keys():
            if generic.clearRedirection(k):
                logger.error('Key# %s nothing to clear', k)
                fail += 1
            logger.info('Key# %s reintialisation is done', k)

        if fail:
            return 1
        else:
            return 0
################################################################################