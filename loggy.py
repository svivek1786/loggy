#! /usr/bin/python
#===============================================================================
# File Name           : loggy.py
# Date                : 11-05-2014 v0.1
# Input Files         : def
# Author              : Satheesh <mari.satheesh.paramasivan@oracle.com>
# Description         : Loggy tool draft
#
#===============================================================================
import sys,os,commands,re,getpass,ocpmSsh,cmd,generic
import loggerRecord,globalS
import argparse

#parse the run-time args passed
parser = argparse.ArgumentParser(description='  To get the mra.log,rc.log,\
        qpTraces & tcpdump to the log viewer machine or any user defined server\
        all in one place with a single click. Works among multiple Active Pairs \
        (MPE\'s, MRA\'s)..................................................\
        Example: ./loggy CAM-92410 -c serverRack_C6GRsetup.cfg or ./loggy \
        CAM-92410 or ./loggy -v ',add_help=True)
parser.add_argument('testName',help='Name suffixed to log file name generated')
#if the def file is not passed as arg thn take the default file.
parser.add_argument('-c', '--config',default='serverRack.def',help='definition file')
parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.37')
parser.add_argument("-d", "--debug", help="Enable standard output verbosity(default Yes in Beta testing)",action="store_false")
args = parser.parse_args()


#to avoid invoking class via object everytime copy to local variablesG
testCaseName = args.testName
scrDefFile = args.config

#==============================================================================#
#               Sourcing testbed specific config file                          #
#==============================================================================#
execfile(scrDefFile)

#==============================================================================#
#           Opening log file to record all the cli outputs                     #
#==============================================================================#
globalS.init()#intialize the global variables
generic      = generic.generic()

############################################################################
#Function Name  : compileFileName                                          #
#Input          : Nil                                                      #
#Return Value   : just sets the suffix fileName for logs                   #
############################################################################
def compileFileName():
    dayTime      = generic.dateTimeFields()
    dayTime     += '_' + testCaseName
    return dayTime
############################################################################

sufFileName = compileFileName()
logFileName  = "/tmp/loggyTool" + "_" + sufFileName + ".log"
logger       = loggerRecord.loggerInit(logFileName)
logger.debug('Log file# %s & TestBed file is %s',logFileName,scrDefFile)
#currently this is not working debug later
if args.debug:
    logger.setLevel('DEBUG')

#create an Object for ocpmSsh
ssh = ocpmSsh.ocpmSsh()
cmpObj = ssh.sshServer(OCPMTestbench['CMP_IP'], OCPMTestbench['CMP_UserName'], OCPMTestbench['CMP_Pswd']);
ipList = ssh.addrProdCorr(cmpObj)

#remove the first IP as it belongs to CMP from where we no longer required any log as of now
ipList.remove(ipList[0])
logger.debug("IP's retrived are %s",ipList)

for ip in ipList:
    logger.debug('IP to login is %s',ip)
    #username & password are hard coded below line
    s2 = ssh.sshServer(ip, OCPMTestbench['CMP_UserName'], OCPMTestbench['CMP_Pswd']);

############################################################################
#Function Name  : qpTraceMenu                                              #
#Input          : Nil                                                      #
#Return Value   : choice ie character that the user is inputed             #
############################################################################
def qpTraceMenu():
    ''' print menu called whenever there is user option required
    '''
    logger.info('\n\n=========================>Hi! Im Loggy <=================================\
                \n\t1. press \'1\' to fetch qptrace from MRA\
                \n\t2. press \'2\' to fetch QPTRACE from MPE\
                \n\t3. press \'3\' to fetch QPTRACE from CMP\
                \n\tb. press \'b\' to go to previous menu\
                \n**********************Im Waiting for ur Highness!**********************\n')
    choice = raw_input("What would you like to do (press b to previous menu)# ")
    return choice
############################################################################

############################################################################
#Function Name  : printMenu                                                #
#Input          : Nil                                                      #
#Return Value   : choice ie character that the user is inputed             #
############################################################################
def printMenu():
    ''' print menu called whenever there is user option required
    '''
    logger.info('\n\n=========================>Hi! Im Loggy <=================================\
                \n\t1. press \'1\' to get MRA Log\
                \n\t2. press \'2\' to fetch rc log\
                \n\t3. press \'3\' to fetch both MRA & MPE log\
                \n\t4. press \'4\' to edit the test case name\
                \n\t5. press \'5\' Enter qptrace Sub-Menu\
                \n\t6. press \'6\' to start tcpdump in MRA\
                \n\t7. press \'7\' to start tcpdump in MPE\
                \n\t8. press \'8\' to start tcpdump in both MRA & MPE\
                \n\ta. press \'a\' to log all qp_log, qp_trace & tcpdump in MPE & MRA \
                \n\ts. press \'s\' to scp logs\
                \n\tr. press \'r\' to reintialise the loggy\
                \n\tq. press \'q\' to quit loggy\
                \n**********************Im Waiting for ur Highness!**********************\n')
    choice = raw_input("What would you like to do (press q to quit)# ")
    return choice
############################################################################

choice = printMenu()

while choice != 'q':
    if choice == '1':
        logger.info("You chose 1 so redirecting MRA log")
        ssh.detectMulDevRedirect('MRA',sufFileName,'qpLog')
    elif choice == '2':
        logger.info("You chose 2 so redirecting MPE log")
        ssh.detectMulDevRedirect('MPE',sufFileName,'qpLog')
    elif choice == '3':
        typeLog = 'qpLog'
        logger.info("You chose 3 so redirecting both MRA & MPE log")
        ssh.detectMulDevRedirect('MRA',sufFileName,typeLog)
        ssh.detectMulDevRedirect('MPE',sufFileName,typeLog)
    elif choice == '4':
        logger.info("You choose 4 updating the test case Name[%s]",testCaseName)
        testCaseTmpName = raw_input("Enter the Test Case Name# ")
        if testCaseTmpName != "":
            testCaseName = testCaseTmpName
            sufFileName = compileFileName()
    elif choice == '5':
        logger.info("You chose 5 so entering QPTRACE sub-menu")
        qpChoice = qpTraceMenu()
        typeLog = 'qpTrace'
        while choice != 'b':
            if qpChoice == '1':
                logger.info("You chose 1 so redirecting MRA's QPTRACE")
                ssh.detectMulDevRedirect('MRA',sufFileName,typeLog)
            elif qpChoice == '2':
                logger.info("You chose 2 so redirecting MPE's QPTRACE")
                ssh.detectMulDevRedirect('MPE',sufFileName,typeLog)
            elif qpChoice == '3':
                logger.info("You chose 3 so redirecting CMP's QPTRACE")
                ssh.detectMulDevRedirect('CMP',sufFileName,typeLog)
            elif qpChoice == 'b':
                logger.debug('Breaking the sub-menu')
                break
            elif choice == 'q':
                logger.info("You chose to quit")
                ssh.sshClose();
            else:
                logger.info ("That is not a valid input.")
            qpChoice = qpTraceMenu()
    elif choice == '6':
        logger.info("You chose 6 so redirecting MRA tcpdump")
        ssh.detectMulDevRedirect('MRA',sufFileName,'tcpdump')
    elif choice == '7':
        logger.info("You chose 7 so redirecting MRA tcpdump")
        ssh.detectMulDevRedirect('MPE',sufFileName,'tcpdump')
    elif choice == '8':
        logger.info("You chose 8 so redirecting both MPE & MRA tcpdump")
        ssh.detectMulDevRedirect('MRA',sufFileName,'tcpdump')
        ssh.detectMulDevRedirect('MPE',sufFileName,'tcpdump')
    elif choice == 'a':
        logger.info("You chose a so redirecting both MPE & MRA tcpdump")
        typeLogList = ['qpLog','qpTrace','tcpdump']
        for typeLog in typeLogList:
            logger.info("Redirecting %s in MRA & MPE",typeLog)
            ssh.detectMulDevRedirect('MRA',sufFileName,typeLog)
            ssh.detectMulDevRedirect('MPE',sufFileName,typeLog)
    elif choice == 'd':
        logger.info("You chose d")
        ssh.dictDumper()
    elif choice == 'c':
        logger.info("You chose c")
        ssh.dictDumper()
    elif choice == 'r':
        logger.info("You chose r to reintialise the operation")
        ssh.reinitialisation()
        sufFileName = compileFileName()
    elif choice == 's':
        logger.info("You chose s so SCP'ing the logs")
        ssh.scpFiles(OCPMTestbench['logServerIP'],OCPMTestbench['logServerUserName'],OCPMTestbench['logServerPswd'],OCPMTestbench['logServerPath'])
        sufFileName = compileFileName()
    elif choice == 'q':
        logger.info("You chose to quit")
        ssh.sshClose();
    else:
        logger.info ("#############################")
        logger.info ("# That is not a valid input #")
        logger.info ("#############################")
    choice = printMenu()

logger.info('Thanks for using loggy!welcome again!')
sys.exit(0)

################################################################################
#v1.0 Released
#v1.1 added multiple active MEP&MRA support
#v1.2 added IP from OAM VIP fixed test case name
#v1.21 ping test before connecting
#v1.22 support for qptrace,multiple file SCP, killing the particular process etc
#v1.3 supports for  tcpdump for active MPE&MRA, Option 'a' for all the traces
#     (qptrace,qplog,tcpdump) at once.
#v1.31 pid regexp is fixed
#v1.32 testcasename & clearRedirectionis fixed 2/16/15
#v1.33 aftr scp filename is regenerated & logger.error print is removed 2/24/15
#v1.34 increased the cmd timeout as scp takes nearly 60s for paswd prompt
#v1.35 appRev cmd is now logged
#v1.36 reinitialisation is added
#v1.37 after reinitialisation framing new stamp is added
