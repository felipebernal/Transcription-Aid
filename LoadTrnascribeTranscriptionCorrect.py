# -*- coding: utf-8 -*-
"""
Created on Wed Jul 13 11:05:43 2016

@author: bernalarangofa
"""

import tkinter as tki
import tkinter.messagebox
import tkinter.filedialog

from os import path, makedirs
from os import name as osname
from os import startfile as osstartfile
#import pickle
from pickle import dump as pickledump
from pickle import load as pickleload


from pydub import AudioSegment
from pydub.playback import play
from threading import Thread
#import numpy as np
from numpy import array as nparray
from numpy import histogram as nphistogram
from numpy import std as npstd
from numpy import mean as npmean
from numpy import mod as npmod
from numpy import floor as npfloor

#from PIL import Image, ImageTk

import text2pdffunction
import text2DOC
from pydub.silence import split_on_silence
from pydub.silence import detect_nonsilent
from pydub.silence import detect_silence
#import TranscriAndwriteNoInternet
import speech_recognition as sr

#import webbrowser
from  webbrowser import open as webbrowseropen
import sys
import subprocess



# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    application_path =sys._MEIPASS
    programpath=path.dirname(sys.executable)
    print('Basic path frozen:')
    print(programpath)
elif __file__:
    application_path = path.dirname(__file__)
    programpath=application_path
    print('path not frozen:')
    print(__file__)



pathdata=path.join(programpath,"data")
pathkpoints=path.join(programpath,"data","kpoints.points")
if not path.exists(pathdata):
    makedirs(pathdata)
    kpointsini=0
    karmapointsfile=open(pathkpoints,'wb')
    pickledump(kpointsini, karmapointsfile)
    karmapointsfile.close()
else:
    try:
        karmapointsfile=open(pathkpoints,'rb')
        kpointsini=pickleload(karmapointsfile)
        karmapointsfile.close()
    except:
        kpointsini=0

#first check if you are using windows or mac or linux
optsys=osname
if optsys=='nt':
    config_name = 'ffmpeg\\bin\\ffmpeg.exe'
    config_path = path.join(application_path, config_name)
    AudioSegment.converter = config_path
    pathjoiner='\\'
    #AudioSegment.converter = "ffmpeg\\bin\\ffmpeg.exe"
elif (optsys=='mac')|(optsys=='posix'):
    config_name = 'ffmpeg/ffmpeg'
    config_path = path.join(application_path, config_name)
    AudioSegment.converter = config_path
    pathjoiner='/'    
    #AudioSegment.converter = "ffmpeg\\bin\\ffmpeg.exe"
    
class simpleapp_tk(tki.Tk):
    def __init__(self,parent):
        tki.Tk.__init__(self,parent)
        self.parent = parent
        self.positions=[0,0]
        self.kpoints=kpointsini
        self.numfiles=1
        self.filetranscribed=0
        self.filechosen=0
        self.checkfinal=0
        self.initime=0
        self.totaltext=''
        self.num=self.positions[0]
        self.corrected=self.positions[1]
        self.initialize()
        self.routine()
        

    def initialize(self):
        self.grid()
        
        #self.entry = tki.Entry(self)
        #self.entry.grid(column=0,row=0,sticky='EW')
        
        w=800
        h=100
        # create a Frame for the Text and Scrollbar
        txt_frm = tki.Frame(self, width=w, height=h)
        txt_frm.pack(fill="both", expand=True)
        ## implement stretchability
        txt_frm.grid_rowconfigure(1, weight=1)
        txt_frm.grid_rowconfigure(2, weight=1)
        txt_frm.grid_rowconfigure(3, weight=0)
      
        
        txt_frm.grid_columnconfigure(1, weight=1)      
        txt_frm.grid_columnconfigure(2, weight=1)      
        txt_frm.grid_columnconfigure(3, weight=1)
        txt_frm.grid_columnconfigure(4, weight=1)      
        txt_frm.grid_columnconfigure(5, weight=1)
        txt_frm.grid_columnconfigure(6, weight=1)
        txt_frm.grid_columnconfigure(7, weight=1)      
        txt_frm.grid_columnconfigure(8, weight=1)      
        txt_frm.grid_columnconfigure(9, weight=1)      
        txt_frm.grid_columnconfigure(10, weight=1)      
        txt_frm.grid_columnconfigure(11, weight=0)      
        
        
        #create frame for the file options
        #txt_frm2= tki.Frame(txt_frm, width=w, height=10)
        #txt_frm2.pack(fill="both", expand=True)
        
        # create a button to choose a file
        self.button = tki.Button(txt_frm,text=u"File",
                                command=self.OnButtonClick)
        self.button.grid(column=0,row=0, sticky="NEW")
        
        # create a button to transcribe the file
        self.buttonTrans = tki.Button(txt_frm,text=u"Aut. Transcription",
                                command=self.OnButtonTranscribe)
        self.buttonTrans.grid(column=0,row=1, sticky="NEW")
        
        # create a button with an about
        self.buttonAbout = tki.Button(txt_frm,text=u"?",
                                command=self.OnButtonAbout)
        self.buttonAbout.grid(column=11,row=0, sticky="NW")         
        
        # create a button to save a file
        self.buttonsave = tki.Button(txt_frm,text=u"Save",
                                command=self.OnButtonsaveClick)
        self.buttonsave.grid(column=1,row=0, sticky="NEW")
        
        # create a button to export the transcription
        self.buttonExport = tki.Button(txt_frm,text=u"Export",
                                command=self.OnButtonExport)
        self.buttonExport.grid(column=1,row=1, sticky="NEW")
        
        # create a button to export the transcription
        self.buttontime = tki.Button(txt_frm,text="Initial time (s)",
                                command=self.OnButtonInitialTimeread)
        self.buttontime.grid(column=0,row=3, rowspan=2,sticky="NSEW")  
        
        
        # create a Text widget for the corrected text
        self.txtcorr = tki.Text(txt_frm, borderwidth=3, relief="sunken")
        self.txtcorr.config(font=("consolas", 12), undo=True, wrap='word')
        self.txtcorr.grid(row=1, column=2,columnspan=8,rowspan=1, sticky="nsew", padx=2, pady=2) 
        
         # create a Scrollbar and associate it with txtcorr
        scrollb = tki.Scrollbar(txt_frm, command=self.txtcorr.yview)
        scrollb.grid(row=1, column=11, sticky='nsew')
        self.txtcorr['yscrollcommand'] = scrollb.set
         
        
        # create a Text widget for the sentences that need to be corrected
        self.txt = tki.Text(txt_frm, borderwidth=3, relief="sunken")
        self.txt.config(font=("consolas", 12), undo=True, wrap='word')
        self.txt.grid(row=2, column=2,columnspan=10,rowspan=1, sticky="nsew", padx=2, pady=2)
        
        # create a Text widget for defining the initial time
        #self.txttimetext = tki.Label(txt_frm,text="Initial time (s)" ,borderwidth=1, relief="sunken")
        self.txttime = tki.Entry(txt_frm, borderwidth=1, relief="sunken")
        #self.txttime.config(font=("consolas", 12), undo=True, wrap='word')
        #self.txttimetext.grid(row=3, column=0,columnspan=1,rowspan=1, sticky="sew", padx=1, pady=1)
        self.txttime.grid(row=4, column=0,columnspan=1,rowspan=1, sticky="nsew", padx=1, pady=1)
        self.txttime.insert(0, 0)
        
        
        

        #label with isntructions program
        self.lbl3=tki.Label(txt_frm, text="Instructions:\n -First press the button 'File' and locate the mp3 file\n"+
        "-Check the 'Fast Internet' checkbox if you want to use\n Google speech recognition to help with the transcription.\n Uncheck it if you do not have internet connection\n (Sphinx recognition used).\n"+
                                            "-Press Aut. Transcription if it is the first time you use this file.\n"+
                                            "-After the transcription is finalized you can start correcting it.\n"                                            
                                            "-If you want to save the work done so far press 'Save'.\n"+
                                            "-To see your work as doc or pdf press 'Export'.\n")                
        self.lbl3.grid(column=0,row=2, sticky="NEW",columnspan=2)  
        
        
        #creat a label with the positions of correctedness
        self.v=tki.StringVar()   
        self.v.set("position: "+ str(self.positions[0])+" corrected: "+str(self.positions[1])+ " out of: "+ str(self.numfiles))   
        self.lbl=tki.Label(txt_frm, textvariable=self.v)                
        #self.lbl=tki.Button(txt_frm, textvariable=self.v)                
        self.lbl.grid(column=0,row=3, sticky="NW",columnspan=2)
        #self.lbl.pack()
        
        
        #label with isntructions comands
        self.lbl2=tki.Label(txt_frm, text="Repeat audio: 'shift arrow-up'   Continue: 'shift arrow-down'\n Go back: 'Esc'")                
        #self.lbl=tki.Button(txt_frm, textvariable=self.v)                
        self.lbl2.grid(column=9,row=3, sticky="NW")
        
        #creat a label with messages from the program
        self.messageV=tki.StringVar()   
        self.messageV.set("")   
        self.lbl5=tki.Label(txt_frm, textvariable=self.messageV)                
        #self.lbl=tki.Button(txt_frm, textvariable=self.v)                
        self.lbl5.grid(column=2,row=0, sticky="NEW",columnspan=7)
        #self.lbl.pack()
    
        #create a checkbutton that asks if people have a fast internet conection
        self.Vinterenet=tki.IntVar()
        #self.checkbuttonInternet=tki.Checkbutton(self,text="Fast Internet",variable=self.Vinterenet)
        self.checkbuttonInternet=tki.Checkbutton(txt_frm,text="Fast Internet",variable=self.Vinterenet)
        self.Vinterenet.set(1)
        #.grid(row=2, sticky="W")
        self.checkbuttonInternet.grid(column=0,row=5,sticky="NEW",columnspan=1)
        #self.checkbuttonInternet.pack(side="left")
    
    
    
        #creat a label with number of karma points
        self.kpointslabel=tki.StringVar()   
        self.kpointslabel.set("Kpoints: "+ str(self.kpoints))   
        self.lbl4=tki.Label(txt_frm, textvariable=self.kpointslabel)                
        #self.lbl=tki.Button(txt_frm, textvariable=self.v)
        #self.lbl4.pack(side="left")                
        self.lbl4.grid(column=9,row=5, sticky="NE",columnspan=1)
        
#        #laberl with photo    
#        image = Image.open("Manjushri.jpg")
#        [imageSizeWidth, imageSizeHeight] = image.size
#        n=0.25
#        newImageSizeWidth = int(imageSizeWidth*n)
#        newImageSizeHeight = int(imageSizeHeight*n) 
#        image = image.resize((newImageSizeWidth, newImageSizeHeight), Image.ANTIALIAS)
#        photo = ImageTk.PhotoImage(image)
#        self.w = tki.Label(txt_frm, image=photo)
#        self.w.photo = photo    
#        self.w.grid(column=0,row=1, sticky="NW",columnspan=2)   
    
    
        #Create empty label for strechability
#        self.streched=tki.StringVar()   
#        self.streched.set("v ")
#        self.lbl3=tki.Label(txt_frm, textvariable=self.streched)                
#        #self.lbl=tki.Button(txt_frm, textvariable=self.v)                
#        self.lbl3.grid(column=0,row=2, sticky="WE")    
    
        #self.button.grid_forget()
    
    
        self.resizable(True,True)
        
        #prevent the widget to change size all the time
        self.update()
        self.geometry(self.geometry())
        
        # ensure a consistent GUI size
        txt_frm.grid_propagate(False)
        
    def routine(self):
        #define the events that should happen
        self.txt.bind( "<Shift-Up>", self.playsound)
        self.txt.bind( "<Shift-Down>", self.retrieve_input)
        self.txt.bind( "<Escape>", self.Goback)
        self.txt.bind("<Destroy>", self.on_closing)        
        
    
  
       
    def OnButtonExport(self):     
        if self.filechosen==1:
            self.exportstuff()
    
    def OnButtonTranscribe(self):
        if self.filechosen==1:
            if self.filetranscribed==0:
                (head,tail)=path.split(self.file_path)
                #filenamewithext=tail
                (head2,tail2)=path.splitext(tail)
                filename=head2
                #pathfolder=head
                workingdirectory=head
                newdir=workingdirectory+'/'+filename
                if not path.exists(newdir):
                    makedirs(newdir)
                
                #newfolder=splitandsave4TranscrProgram.main(silence_thresh,self.file_path)
                #TranscriAndwrite.main(newfolder)
                self.messageV.set("Loading sound file, this may take some minutes.")
                self.update()
                #t = Thread(target=AudioSegment.from_mp3, args=(self.file_path,))
                #t.start()  
                sound = AudioSegment.from_mp3(self.file_path)
                
                silence_thresh=-55#-45 for normal audio
                min_silence_len=1000#it was 75
                keep_silence=150#it was 75
                minsenttime=1000#4000for lessons
                #maxsenttime=5000
                
                self.messageV.set("Detecting silences in the sound file. This may take several minutes") 
                self.update()
                #self.lbl3.grid(column=2,row=0, sticky="NEW",columnspan=3)
                nosilenceranges = detect_nonsilent(sound, min_silence_len, silence_thresh)
                self.messageV.set("Detecting speech in the sound file. This may take, again, several minutes.") 
                self.update()
                silenceranges = detect_silence(sound, min_silence_len, silence_thresh)
                #chunks = split_on_silence(sound, min_silence_len, silence_thresh,keep_silence=250)
#######          
                not_silence_ranges = detect_nonsilent(sound, min_silence_len, silence_thresh)
                chunks = []
                realnotsilence=[]
                realsilence=[]                
                #oldendi=0
                numsteps=len(not_silence_ranges)
                cnter=0
                switchon=0
                for start_i, end_i in not_silence_ranges:
                    start_i = max(0, start_i - keep_silence)
                       #if cnter==0:
                       #oldendi=end_i
                    
                    end_i += keep_silence
                    
                    if end_i-start_i>=minsenttime and switchon==0: 
                        chunks.append(sound[start_i:end_i])
                        realnotsilence.append([start_i,end_i])
                    elif switchon==0 and cnter!=numsteps-1:
                        #oldendi=end_i
                        oldstarti=start_i
                        switchon=1
                    elif switchon==1:
                        if end_i-oldstarti>=minsenttime:
                            chunks.append(sound[oldstarti:end_i])
                            realnotsilence.append([oldstarti,end_i])
                            switchon=0
                        elif cnter==numsteps-1:
                            chunks.append(sound[oldstarti:end_i])
                            realnotsilence.append([oldstarti,end_i])
                         
                    cnter+=1
                #for i in len(realnotsilence)    
                      
                for index in range(len(realnotsilence)):
                    if index==0:
                        if realnotsilence[0][0]>0:
                            sil_i=0
                            sil_e=realnotsilence[0][0]
                            par=0
                        else:
                            sil_i=realnotsilence[0][1]
                            sil_e=realnotsilence[1][0]
                            par=1
                        realsilence.append([sil_i,sil_e]) 
                    elif par==0:
                        sil_i=realnotsilence[index-1][1]
                        sil_e=realnotsilence[index][0]
                        realsilence.append([sil_i,sil_e])
                    elif par==1 and index<max(ind for ind in range(len(realnotsilence))):
                        sil_i=realnotsilence[index][1]
                        sil_e=realnotsilence[index+1][0]
                        realsilence.append([sil_i,sil_e])
                    
                    
          ######      
                for i, chunk in enumerate(chunks):
                    prgs=((i+1)/len(chunks))*100
                    self.messageV.set("Status silence detection:"+str(prgs)+"%")
                    self.update()
                    chunk.export(newdir+"/chunk{0}.wav".format(i), format="wav")
                numfiles=len(chunks);   
                #free some memory
                sound=None
                chunks=None
                
                audiotimes=open(newdir+"/audiotimes.times",'wb')
                pickledump(realnotsilence, audiotimes)
                audiotimes.close()
                silencetimes=open(newdir+"/silencetimes.times",'wb')
                pickledump(realsilence, silencetimes)
                silencetimes.close()                
                       
                optionint=self.Vinterenet.get()
######################################################################                
                #if self.Vinterenet.get():                
                #    self.messageV.set("There is internet") 
                #    self.update()     
                #else:
                #    self.messageV.set("There is no internet") 
                #    self.update() 
                #TranscriAndwriteNoInternet.main(newdir,optionint)
                
                f=open(newdir+"/audiotimes.times",'rb')
                listtimes=pickleload(f)
                f.close()
                g=open(newdir+"/silencetimes.times",'rb')
                silencetimes=pickleload(g)
                g.close()
                
                timearray=nparray(listtimes)
                silencearray=nparray(silencetimes)
                
                deltasilencetimes=silencearray[:,1]-silencearray[:,0]
                #plt.plot(deltasilencetimes,'ro')
                
                #silencetimes for commas and dots in ms
                #siltim=500
                #hist, binedges=nphistogram(deltasilencetimes,siltim)
                #plt.plot(binedges[1:],hist)
                maxcomatimes=400#npmean(deltasilencetimes)+npstd(deltasilencetimes)
                #maxdottimes=600
                maxreturn=1000
                #logicomas=deltasilencetimes<=maxcomatimes
                #logidots=(deltasilencetimes<=(maxcomatimes+npstd(deltasilencetimes)))&(deltasilencetimes>maxcomatimes)
                #logireturn=(deltasilencetimes>(maxcomatimes+npstd(deltasilencetimes)))
                
                logicomas=deltasilencetimes<=maxcomatimes
                logidots=(deltasilencetimes<=maxreturn) &(deltasilencetimes>maxcomatimes)
                logireturn=(deltasilencetimes>maxreturn)
                
                if optionint:
         
                    textGoogle='';
                    
                    listGoogle=list(range(numfiles))
                    
                    notrecoGoog=[]
                    
                    beginsilence=(timearray[0,0]-silencearray[0,0])>0
                    
                    if beginsilence:
                        depha=1
                    else:
                        depha=0
                        
                     #open a file were to write the recognition
                    
                    nemtext2=path.join(newdir,'textchunksgoogle.txt')
                       
                        
                    
                    for num in range(0,numfiles):
                        print(num)
                        self.messageV.set("Google recognition: "+ str((num+1)/numfiles*100)+"%") 
                        self.update()
                    #num=5;
                        namefile="chunk"
                        filenum=namefile+'%d' % num+'.wav'
                        #filefolder=newdir
                        filepat=newdir+pathjoiner+filenum
                    #print(filepat)
                     
                    #AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "english.wav")
                    #AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "testfolder\\chunk7.wav")
                        AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), filepat)
                        #AUDIO_FILE = AUDIO_FILE.decode('utf-8').encode("latin-1")
                    #AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "french.aiff")
                    #AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "chinese.flac")
                    #check if there should be a comma a dot or a return
                        if num+depha==numfiles-1:
                            print(num)  
                            
                        if num+depha<=numfiles-1 &len(logicomas)>num+depha:
                            if logicomas[num+depha]:
                                separator=', '
                            elif logidots[num+depha]:
                                separator='. '
                            elif logireturn[num+depha]:
                                separator='.\n\n'
                        else:
                            separator='.\n\n'
                    # use the audio file as the audio source
                        r = sr.Recognizer()
                        with sr.AudioFile(AUDIO_FILE) as source:
                    #with sr.AudioFile('C:\\Users\\felipe bernal arango\\Desktop\\speechrecognition\\english.wav') as source:    
                            audio = r.record(source) # read the entire audio file
                    
                    # recognize speech using Google Speech Recognition
                        try:
                        # for testing purposes, we're just using the default API key
                        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
                        # instead of `r.recognize_google(audio)`
                        #print("Google Speech Recognition thinks you said " + r.recognize_google(audio))
                            recogoo=r.recognize_google(audio)
                            listGoogle[num]=[recogoo,listtimes[num],separator]
                            textGoogle=textGoogle+separator+recogoo
                            filetextGoogle=open(nemtext2,'a')
                            filetextGoogle.write(recogoo+separator)
                            filetextGoogle.close()
                           # textGoogle.extend(textgoo)
                        except sr.UnknownValueError:
                                #print("Google Speech Recognition could not understand audio")
                                self.messageV.set("Google Speech Recognition could not understand audio") 
                                self.update()
                                notrecoGoog.append(num)
                                listGoogle[num]=["",listtimes[num],separator]
                        except sr.RequestError as e:
                                #print("Could not request results from Google Speech Recognition service; {0}".format(e))
                                self.messageV.set("Could not request results from Google Speech Recognition service; {0}".format(e)) 
                                self.update()
                    
                    #audiogoogle=open(newdir+"/Googlerecognition.recogtimes",'wb')
                    audiogoogle=open(newdir+"/Textrecognition.recogtimes",'wb')
                    pickledump(listGoogle, audiogoogle)
                    audiogoogle.close()
                    
                    
                    #Noaudiogoogle=open(newdir+"/GoogleNorecognized.recogtimes",'wb')
                    Noaudiogoogle=open(newdir+"/TextNorecognized.recogtimes",'wb')
                    pickledump(notrecoGoog, Noaudiogoogle)
                    Noaudiogoogle.close()
                    
                    print(textGoogle)
                
                else:
                        
                        
                        
                    textSphinx='';
                   
                    listSphinx=list(range(numfiles))
                    
                    notrecoSph=[];
                    
                    
                    beginsilence=(timearray[0,0]-silencearray[0,0])>0
                    
                    if beginsilence:
                        depha=1
                    else:
                        depha=0
                        
                     #open a file were to write the recognition
                    nemtext1=path.join(newdir,'textchunksSPHINX.txt')
                               
                    
                    for num in range(0,numfiles):
                        print(num)
                        self.messageV.set("Sphinx recognition: "+ str((num+1)/numfiles*100)+"%") 
                        self.update()
                    #num=5;
                        namefile="chunk"
                        filenum=namefile+'%d' % num+'.wav'
                        #filefolder=newdir
                        filepat=newdir+pathjoiner+filenum
                    #print(filepat)
                    
                    
                    
                    
                    #AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "english.wav")
                    #AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "testfolder\\chunk7.wav")
                        AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), filepat)
                        #AUDIO_FILE = AUDIO_FILE.decode('utf-8').encode("latin-1")
                    #AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "french.aiff")
                    #AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "chinese.flac")
                    #check if there should be a comma a dot or a return
                        if num+depha<=numfiles-1:
                            if logicomas[num+depha]:
                                separator=', '
                            elif logidots[num+depha]:
                                separator='. '
                            elif logireturn[num+depha]:
                                separator='.\n\n'
                        else:
                            separator='.\n\n'
                        
                    # use the audio file as the audio source
                        r = sr.Recognizer()
                        with sr.AudioFile(AUDIO_FILE) as source:
                    #with sr.AudioFile('C:\\Users\\felipe bernal arango\\Desktop\\speechrecognition\\english.wav') as source:    
                            audio = r.record(source) # read the entire audio file
                    
                    # recognize speech using Sphinx
                        try:
                       # print("Sphinx thinks you said " + r.recognize_sphinx(audio))
                            recosph=r.recognize_sphinx(audio)
                            listSphinx[num]=[recosph,listtimes[num],separator]
                            textSphinx=textSphinx+separator+recosph
                            filetextSPHINX=open(nemtext1,'a')
                            filetextSPHINX.write(recosph+separator)
                            filetextSPHINX.close()
                            #textSphinx.extend(textsph)
                        except sr.UnknownValueError:
                                print("Sphinx could not understand audio")
                                self.messageV.set("Sphinx could not understand audio") 
                                self.update()
                                notrecoSph.append(num)
                                listSphinx[num]=["",listtimes[num],separator]
                        except sr.RequestError as e:
                                print("Sphinx error; {0}".format(e))
                                self.messageV.set("Sphinx error; {0}".format(e)) 
                                self.update()
                    
                    
                    
                    #audiosphinx=open(newdir+"/Sphinxrecognition.recogtimes",'wb')
                    audiosphinx=open(newdir+"/Textrecognition.recogtimes",'wb')
                    pickledump(listSphinx, audiosphinx)
                    audiosphinx.close()
                    
                    #Noaudiosphinx=open(newdir+"/SphinxNorecognized.recogtimes",'wb')
                    Noaudiosphinx=open(newdir+"/TextNorecognized.recogtimes",'wb')                    
                    pickledump(notrecoSph, Noaudiosphinx)
                    Noaudiosphinx.close()
                    print(textSphinx)                
                self.messageV.set("Ready. Start transcription correction") 
                self.update()
                
######################################################################             
                self.filetranscribed=1
                self.Initializetranscriptedfile()
               #self.transcribestff()
        
    def OnButtonClick(self):
  
        #First choose the file
        #self.workingfolder=tkinter.filedialog.askdirectory() 
        ####
        self.file_path = tkinter.filedialog.askopenfilename(filetypes=[("MP3","*.mp3")])
        (head,tail)=path.split(self.file_path)
        (head2,tail2)=path.splitext(tail)
        self.workingfilename=head2        
        self.workingfolder=head+'/'+head2
        #####        
        self.filechosen=1
        namefiletranscr=self.workingfolder+"/Textrecognition.recogtimes"
        if path.isfile(namefiletranscr):
            self.filetranscribed=1
            self.Initializetranscriptedfile()
        else:
            self.messageV.set("File chosen but not yet transcribed.\n Please start automatic transcription with the button Aut. Transcription")
            self.update()            
            #self.lbl3.grid(column=2,row=0, sticky="NEW",columnspan=4,rowspan=2)
            
        #check if the file was alredy processed
        
        
        #num=0
        #corrected=0
        #workingfolder='testfolder'
        #workingfolder2="C:\Users\\felipe bernal arango\Desktop\speechrecognition\\"+workingfolder
        
    def Initializetranscriptedfile(self):
        
        self.namefile="chunk"

        #Here we load a list with the times of the audio files        
        self.faudiolist=open(self.workingfolder+"/audiotimes.times",'rb')
        self.listtimes=pickleload(self.faudiolist)
        self.faudiolist.close()
        #Here we load a list with the times of the silences        
        self.fsilencelist=open(self.workingfolder+"/silencetimes.times",'rb')
        self.listSilencetimes=pickleload(self.fsilencelist)
        self.fsilencelist.close()

        self.numfiles=len(self.listtimes);
        #f=open("C:\Users\\felipe bernal arango\Desktop\speechrecognition\\"+workingfolder+"/Sphinxrecognition.recogtimes",'rb')
        #audiosphinxtrans=pickle.load(f)
        #f.close()
        
        
        self.fname=self.workingfolder+"/TextrecognitionCorrected.recogtimes"
        if path.isfile(self.fname):
            #open the corrected file
            self.filecorr=open(self.workingfolder+"/TextrecognitionCorrected.recogtimes",'rb')
            self.listGoogle=pickleload(self.filecorr)
            self.filecorr.close()
            self.audiogoogletrans=self.listGoogle
            self.posfile=open(self.workingfolder+"/PositionCorrectiond.pos",'rb')
            self.positions=pickleload(self.posfile)
            self.num=self.positions[0]
            self.corrected=self.positions[1]
            self.posfile.close()
############################            
            self.filetxtcorr = open(path.join(self.workingfolder,self.workingfilename+'corr.txt'), 'rb')
            self.totaltext=self.filetxtcorr.read()
            self.filetxtcorr.close()
            self.clear_textcorr()
            self.txtcorr.insert('1.0',self.totaltext)
###########################            
            #if it doesn't exist then create it
            #posfile=    
        else:
            self.g=open(self.workingfolder+"/Textrecognition.recogtimes",'rb')
         #   g=open("C:\Users\\felipe bernal arango\Desktop\speechrecognition\\"+workingfolder+"/Sphinxrecognition.recogtimes",'rb')
            self.audiogoogletrans=pickleload(self.g)
            self.g.close()
            #listSphinx=range(numfiles)
            self.listGoogle=self.audiogoogletrans
            self.positions=[0,0]
            
            self.filetxtcorr = open(path.join(self.workingfolder,self.workingfilename+'corr.txt'), 'w+')
            self.filetxtcorr.close()
                        
#############################            
            #self.filetxtcorr = open(path.join(self.workingfolder,self.workingfilename+'corr.txt'), 'r+')
###############################        
        
        self.v.set("position: "+ str(self.positions[0])+" corrected: "+str(self.positions[1])+ " out of: "+ str(self.numfiles-1))
        self.writetextbasic(self.positions[0])
        self.playsoundbasic(self.positions[0])
    
    
    
    def OnButtonsaveClick(self):
        if self.filechosen==1& self.filetranscribed==1:        
            self.savestuff
            self.messageV.set("Your transcription and correction have been saved")
        
    def OnButtonInitialTimeread(self):
        self.initime = self.txttime.get()                
        
        
    
    def OnButtonAbout(self):
        tkinter.messagebox.showinfo("About", "This program was plugged together based on the kind help from hundreds of internet blogs on how to program in python "+
        "and how to use the speech recognition package.\n This effort was undertaken thanks to the inspiration and kindness received from Lama Alan Wallace.\n May his teachings reach all sentient beings.\n"+ 
        "Questions can be directed to feberna@gmail.com\n This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License")    
    
    
    
    def writetextbasic(self,indnum):
        templist=self.audiogoogletrans[indnum]
        tipo=type(templist)
        nada=' '
        if tipo==int:
            self.txt.insert('1.0',nada)
        elif tipo==list:
            self.txt.insert('1.0',templist[0])
            
    def playsoundbasic(self,indnum):
        filenum=self.namefile+'%d' % indnum+'.wav'
        soundtext = AudioSegment.from_wav(self.workingfolder+pathjoiner+filenum)
        #play(soundtext)
        t = Thread(target=play, args=(soundtext,))
        t.start()      
    
    def playsound(self,event):
        if self.filechosen==1:
            self.playsoundbasic(self.num) 
        
    
    def Goback(self,event):
        if self.num>=1&self.filechosen==1:
        #first get what was writen
#            input = self.txt.get("1.0",'end')
#            templist=self.audiogoogletrans[self.num]
#            self.listGoogle[self.num]=[input,self.listtimes[self.num],templist[2]]
#            self.num-=1
#            self.positions=[self.num,self.corrected]
#            self.clear_text()
#            
#            templist=self.listGoogle[self.num]
#            self.txt.insert('1.0', templist[0])
#            self.playsoundbasic(self.num) 
#            self.v.set("position: "+ str(self.positions[0])+" corrected: "+str(self.positions[1])+ " out of: "+ str(self.numfiles-1))
            input = self.txt.get("1.0",'end')
            templist=self.audiogoogletrans[self.num]
            tipo=type(templist)
            if tipo==list:
                self.listGoogle[self.num]=[input,self.listtimes[self.num],templist[2]]
                self.num-=1
                self.clear_text()
            elif tipo==int:
                #find the time from the notrecognized times            
                #todo! find the not recognized ones and put them in so that the human recognizes them
                #here we only need to give a time to the not recognized thing           
                self.listGoogle[self.num]=[input,self.listtimes[self.num],0]
                self.num-=1
                self.clear_text()
            
        #Add the text 
            templist=self.listGoogle[self.num]
            self.txt.insert('1.0', templist[0])
            self.playsoundbasic(self.num) 
            #self.v.set("position: "+ str(self.positions[0])+" corrected: "+str(self.positions[1])+ " out of: "+ str(self.numfiles-1))
            self.v.set("position: "+ str(self.num)+" corrected: "+str(self.positions[1])+ " out of: "+ str(self.numfiles-1))
            
            self.update()
         

    def clear_text(self):
        self.txt.delete('1.0', 'end')
        
    def clear_textcorr(self):
        self.txtcorr.delete('1.0', 'end') 
    
    def retrieve_input(self,event):
        if self.filechosen==1 & self.filetranscribed==1:
            self.messageV.set("")
            self.update() 
            self.kpoints+=1
        #we read how the user has changed the complete text    
            self.totaltext = self.txtcorr.get("1.0",'end')
        #First get what the user has written in the text space            
            if (self.num >= self.numfiles-1):
                #if (self.checkfinal==0):
                input = self.txt.get("1.0",'end')
                templist=self.audiogoogletrans[self.num]
                tipo=type(templist)
                if tipo==list:
                    self.listGoogle[self.num]=[input,self.listtimes[self.num],templist[2]]
                    self.savestuff()
                    self.checkfinal=1
                    #self.clear_text()
                    #self.root.destroy()
                elif tipo==int:
                    #find the time from the notrecognized times            
                    #todo! find the not recognized ones and put them in so that the human recognizes them
                    #here we only need to give a time to the not recognized thing           
                    self.listGoogle[self.num]=[input,self.listtimes[self.num],0]
                    self.savestuff()
                    self.checkfinal=1
                    self.root.destroy()
                self.totaltext=self.totaltext.rstrip('\n')+self.delimiter(self.num)+input.strip()
                #After having read the text that the user fixed we put it int he first text box
                self.clear_textcorr()
                self.txtcorr.insert('1.0',self.totaltext)
                self.txtcorr.see('end')
                self.update() 
            else:   
                self.finalfinal()  
                input = self.txt.get("1.0",'end')
                templist=self.audiogoogletrans[self.num]
                tipo=type(templist)
                if tipo==list:
                    self.listGoogle[self.num]=[input,self.listtimes[self.num],templist[2]]
                    self.num+=1
                    self.clear_text()
                elif tipo==int:
                    #find the time from the notrecognized times            
                    #todo! find the not recognized ones and put them in so that the human recognizes them
                    #here we only need to give a time to the not recognized thing           
                    self.listGoogle[self.num]=[input,self.listtimes[self.num],0]
                    self.num+=1
                    self.clear_text()
                if (input!='\n') or (input.strip !='\n') or (input.strip !='')or (input.rstrip(' ') !=''):
                    self.totaltext=self.totaltext.rstrip('\n')+input.strip()+self.delimiter(self.num)
                #After having read the text that the user fixed we put it int he first text box
                self.clear_textcorr()
                self.txtcorr.insert('1.0',self.totaltext)
                self.txtcorr.see('end')
                self.update() 
         #Now insert the new text              
                
                
                if (self.num > self.corrected):
                    templist=self.audiogoogletrans[self.num]
                    tipo=type(templist)
                    nada=' '
                    if tipo==int:
                        self.txt.insert('1.0',nada)
                    elif tipo==list:
                        self.txt.insert('1.0',templist[0])
                    
                    self.playsoundbasic(self.num)
                    self.corrected+=1
                    self.positions=[self.num,self.corrected]
                    
                else:
                    templist=self.listGoogle[self.num]
                    tipo=type(templist)
                    nada=' '
                    if tipo==int:
                        self.txt.insert('1.0',nada)
                    elif tipo==list:
                        self.txt.insert('1.0',templist[0])
                    self.playsoundbasic(self.num)
                    
                self.kpointslabel.set("Kpoints: "+ str(self.kpoints))
                self.v.set("position: "+ str(self.num)+" corrected: "+str(self.positions[1])+ " out of: "+ str(self.numfiles-1))  
                self.savingauto
                
     
    def on_closing(self,event):
        if self.filechosen==1 & self.filetranscribed==1:
            audiogoogle=open(self.workingfolder+"/TextrecognitionCorrected.recogtimes",'wb')
            pickledump(self.listGoogle, audiogoogle)
            audiogoogle.close()
            positionssave=open(self.workingfolder+"/PositionCorrectiond.pos",'wb')
            pickledump([self.num,self.corrected], positionssave)
            positionssave.close()
            karmapointsfile=open(pathkpoints,'wb')
            pickledump(self.kpoints, karmapointsfile)
            karmapointsfile.close()
            if (type(self.totaltext)==str):
                self.filetxtcorr=open(path.join(self.workingfolder,self.workingfilename+'corr.txt'), 'w')
                self.filetxtcorr.write(self.totaltext)
                self.filetxtcorr.close()
        


               
    def finalfinal(self):
        if (self.num >= self.numfiles)&self.filechosen==1:
            audiogoogle=open(self.workingfolder+"/TextrecognitionCorrected.recogtimes",'wb')
            pickledump(self.listGoogle, audiogoogle)
            audiogoogle.close()
            positionssave=open(self.workingfolder+"/PositionCorrectiond.pos",'wb')
            pickledump([self.num,self.corrected], positionssave)
            positionssave.close()
            karmapointsfile=open(pathkpoints,'wb')
            pickledump(self.kpoints, karmapointsfile)
            karmapointsfile.close()
            self.quit

    def savingauto(self):
        if npmod(self.num,5)==0 & self.filechosen==1:
#            audiogoogle=open(workingfolder2+"/GooglerecognitionCorrected.recogtimes",'wb')
#            pickle.dump(listGoogle, audiogoogle)
#            audiogoogle.close()
#            positionssave=open(workingfolder2+"/PositionCorrectiond.pos",'wb')
#            pickle.dump([self.num,self.corrected], positionssave)
#            positionssave.close()
            self.savestuff
            
    def savestuff(self):
            audiogoogle=open(self.workingfolder+"/TextrecognitionCorrected.recogtimes",'wb')
            pickledump(self.listGoogle, audiogoogle)
            audiogoogle.close()
            positionssave=open(self.workingfolder+"/PositionCorrectiond.pos",'wb')
            pickledump([self.num,self.corrected], positionssave)
            positionssave.close()
            self.filetxtcorr=open(path.join(self.workingfolder,self.workingfilename+'corr.txt'), 'w')
            self.filetxtcorr.write(self.totaltext)
            self.filetxtcorr.close()
                   
            karmapointsfile=open(pathkpoints,'wb')
            pickledump(self.kpoints, karmapointsfile)
            karmapointsfile.close()
            
    def exportstuff(self):
        text2DOC.main(path.join(self.workingfolder,self.workingfilename+'corr.txt')) 

        if self.listSilencetimes[0][0]==0:
            beginwithsilence=1
        else:
            beginwithsilence=0
        
        numsentences=len(self.listGoogle)        
        filetxt = open(path.join(self.workingfolder,self.workingfilename+'.txt'), 'w')
        #filetxt.write(str(self.workingfilename)+"\n\n\n\n")   

        separatorold=". "
        separatornew=""
        
        textraw0=self.listGoogle[0][0].strip()
        #separator0=str(self.listGoogle[0][2])
        timeaudio0=(self.listGoogle[0][1][1]-self.listGoogle[0][1][0])
        timesilence0=(self.listSilencetimes[0+beginwithsilence][1]-self.listSilencetimes[0+beginwithsilence][0])
   
        accumtime=0
        timedot=900 #this is the time needed to stop putting commas and start putting dots
        timeparag=1500 #this is the time needed to stop putting dots and start making paragraphs
 ###############       
        for n in range(1,numsentences):
            
            templist=self.listGoogle[n]
            tipo=type(templist)
            if tipo==list:
                textraw1=self.listGoogle[n][0].strip()
                #separator1=str(self.listGoogle[n][2])
                
                
                #timeendraw=(self.listGoogle[n][1][1])/1000
                #mintraw=int(npfloor(timeendraw/60))
                #sectraw=int(npfloor((timeendraw-mintraw*60)))
                #milsecraw=int(npfloor((timeendraw-mintraw*60-sectraw)*1000))
                #timeend="["+str(mintraw)+" m:"+ str(sectraw)+" s:"+ str(milsecraw)+" ms"+"]"
                
                timecomma=400
                timedot=600 #this is the time needed to stop putting commas and start putting dots
                timeparag=1000 #this is the time needed to stop putting dots and start making paragraphs
    
                checker=0
                timeendraw=(self.listGoogle[n][1][1])/1000
                mintraw=int(npfloor(timeendraw/60))
                sectraw=int(npfloor((timeendraw-mintraw*60)))
                milsecraw=int(npfloor((timeendraw-mintraw*60-sectraw)*1000))
                timeend="["+str(mintraw)+" m:"+ str(sectraw)+" s:"+ str(milsecraw)+" ms"+"]"                
                
                
                
                timeaudio1=(self.listGoogle[n][1][1]-self.listGoogle[n][1][0])
                #timesilence1=(self.listSilencetimes[n+beginwithsilence][1]-self.listSilencetimes[n+beginwithsilence][0])
                if n<self.numfiles and beginwithsilence==0:        
                    timesilence1=(self.listSilencetimes[n+beginwithsilence][1]-self.listSilencetimes[n+beginwithsilence][0])
                elif n<self.numfiles-1 and beginwithsilence==1: 
                    timesilence1=(self.listSilencetimes[n+beginwithsilence][1]-self.listSilencetimes[n+beginwithsilence][0])
                else:
                    timesilence1=timeparag                
                
                         
                if (textraw0!="")&(textraw1!=""):
                    accumtime=timesilence0
                    if accumtime<=timedot:
                        separator=", "
                        #separatorold=", "
                    elif accumtime>timedot & accumtime<timeparag:
                        separator=". "
                        #separatorold=". "
                    else:
                        separator="."+timeend+"\n"
                        #separatorold=".\n"
                    
                    
                elif (textraw0!="")&(textraw1==""):
                    accumtime=timesilence0
                    separatornew=". "        
                    separator=""                        
                
                elif (textraw0=="")&(textraw1!=""):
                    accumtime+=timesilence0+timeaudio0
                    separator=separatornew
                    if separatornew==". ":             
                        if accumtime<=timedot:
                            separator=", "
                            
                        elif accumtime>timedot & accumtime<timeparag:
                            separator=". "
                            
                        else:
                            separator="."+timeend+"\n"
                            
                elif (textraw0=="")&(textraw1==""):
                    accumtime+=timesilence0+timeaudio0
                    separator=""
                    if separatornew==". ":
                        separatornew="."+timeend+"\n"
                    
                if (separatorold==". ")|("\n" in separatorold):
                    texttowrite=textraw0.capitalize()+separator
                    separatorold=separator
                else:
                    texttowrite=textraw0+separator
                    separatorold=separator
                
                if separatornew!="":
                        separatorold=separator
                    
                filetxt.write(str(texttowrite))
                #separatorold=separator
                textraw0=textraw1
                timesilence0=timesilence1
                timeaudio0=timeaudio1
 #######################  
        texttowrite=textraw0+"."
        filetxt.write(str(texttowrite))    

        filetxt.close()
        
        
        text2DOC.main(path.join(self.workingfolder,self.workingfilename+'.txt'))
        text2pdffunction.main(path.join(self.workingfolder,self.workingfilename+'.txt'))
        pathpdf=path.join(self.workingfolder,self.workingfilename+'.pdf')      
        pathdocx=path.join(self.workingfolder,self.workingfilename+'.docx')
        pathtxt=path.join(self.workingfolder,self.workingfilename+'.txt')
        
        
        self.messageV.set("Your files (docx, pdf and txt) have been created at the location of your mp3")
        
        
        if sys.platform.startswith('darwin'):
            try:
                subprocess.call(('open', pathpdf))
            except:
                try:
                    subprocess.call(('open', pathdocx))
                except:                    
                    subprocess.call(('open', pathtxt))
        elif osname == 'nt':
            try:            
                osstartfile(pathpdf)
            except:
                try:
                    osstartfile(pathdocx)
                except:
                    osstartfile(pathtxt)

        elif osname == 'posix':
            try:
                subprocess.call(('xdg-open', pathpdf))
            except:            
                try:
                    subprocess.call(('xdg-open', pathdocx))
                except:            
                    subprocess.call(('xdg-open', pathtxt))
        
        if 1<0:
            try:
                webbrowseropen(path.join(self.workingfolder,self.workingfilename+'.docx'))
            except:
                try:
                    webbrowseropen(path.join(self.workingfolder,self.workingfilename+'.pdf'))
                except:                
                    webbrowseropen(path.join(self.workingfolder,self.workingfilename+'.txt'))
                
        #########text2pdffunction.main(self.workingfolder+pathjoiner+self.workingfilename+'.txt')
        ########webbrowseropen(self.workingfolder+pathjoiner+self.workingfilename+'.pdf')
        
        




###########################################################
    def delimiter(self,numsentence):
        if self.listSilencetimes[0][0]==0:
            beginwithsilence=1
        else:
            beginwithsilence=0
            
        timecomma=400
        timedot=600 #this is the time needed to stop putting commas and start putting dots
        timeparag=700 #this is the time needed to stop putting dots and start making paragraphs
    
        checker=0
        timeendraw=int(self.initime)+(self.listGoogle[numsentence][1][1])/1000
        mintraw=int(npfloor(timeendraw/60))
        sectraw=int(npfloor((timeendraw-mintraw*60)))
        milsecraw=int(npfloor((timeendraw-mintraw*60-sectraw)*1000))
        timeend="["+str(mintraw)+" m:"+ str(sectraw)+" s:"+ str(milsecraw)+" ms"+"]"
                        
        #timeaudio1=(self.listGoogle[numsentence][1][1]-self.listGoogle[numsentence][1][0])
        if numsentence<self.numfiles and beginwithsilence==0:        
            timesilence1=(self.listSilencetimes[numsentence+beginwithsilence][1]-self.listSilencetimes[numsentence+beginwithsilence][0])
        elif numsentence<self.numfiles-1 and beginwithsilence==1: 
            timesilence1=(self.listSilencetimes[numsentence+beginwithsilence][1]-self.listSilencetimes[numsentence+beginwithsilence][0])
        else:
            timesilence1=timeparag
            
        checker=0
        
        if  timesilence1<=timecomma:
            separator=" "
        elif timesilence1<=timedot:
            separator=", "
            #separatorold=", "
        elif timesilence1>timedot & timesilence1<timeparag:
            separator=". "
            #separatorold=". "
        else:
            separator=". "+timeend+"\n \n"
            checker=1
            #separatorold=".\n"
                
        if (npmod(numsentence,10)==0) and checker==0:
            separator=separator+timeend+' '
             
        
        return separator



###########################################################        
        
if __name__ == "__main__":
    app = simpleapp_tk(None)
    app.title('Transcription-Aid')
    app.mainloop()