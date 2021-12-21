getwd()
# packages
#install.packages('Rcpp', dependencies = TRUE)
Packages <- c("Rcpp", "reshape2", "plyr", "ez", "lattice", "lme4","tidyr","ggplot2", "ggthemes",
              "gridExtra","psych","lmerTest","pequod","QuantPsyc","jtools","reghelper","cowplot",
              "stats","ltm","lsr","apaTables","plotly","Hmisc","interactions","readxl") #"sjstats" not working
new.packages = Packages[!(Packages %in% installed.packages()[,"Package"])]
if(length(new.packages)) install.packages(new.packages)
invisible(lapply(Packages, library, character.only = TRUE))

# read data
rawData = read.csv(file="all_data.csv", header=T)
summary(rawData)
rawData$RT = as.numeric(rawData$rt)
rawData$Subj = mapvalues(rawData$ProlificID, from = unique(rawData$ProlificID),
                         to = 1:length(unique(rawData$ProlificID)))
length(unique(rawData$ProlificID))

# Create refusedFullScreen variable from the button_pressed
# Participants which have an empty column here didn't leave full screen.
# Participants who did leave full screen have a row with the stimulus:
# "The experiment is best in full screen mode, would you agree to switch to full screen?" 
# when 0 is "Yes" and 1 is "No"
refusedFullScreen = subset(rawData,stimulus=="The experiment is best in full screen mode, would you agree to switch to full screen?")
refusedFullScreen$refusedFullScreen = as.factor(refusedFullScreen$button_pressed)

#Completion time
completionTime = subset(rawData,trial_type=="send-data")
completionTime$minutes=completionTime$time_elapsed/60000
mean(completionTime$minutes)
median(completionTime$minutes)
min(completionTime$minutes)
max(completionTime$minutes)

# Demographic Data----
demographicData = ddply(rawData, c("Subj","ProlificID","Gender","Age"), summarise,
                        minutes=time_elapsed[test_part=="comments"]/60000)
length(unique(demographicData$ProlificID))
(100*count(demographicData$Gender=="Female")/length(demographicData$Gender))[2,2]
mean(demographicData$Age)
sd(demographicData$Age)

choiceTrialsforTransitivity = subset(rawData,test_part=="trial")
length(unique(choiceTrialsforTransitivity$Subj))
#write.csv(choiceTrialsforTransitivity,'allChoiceTrialsforTransitivity.csv')


#filter
rawData$Select=rep(1,length(rawData$Subj))
### Exclude unattentive subjects and bots
forfilterData = ddply(rawData, c("Subj","ProlificID","attentionCheck","attCheck2Choice","attCheck2Text","comments","Select"), summarise,
                      minutes=time_elapsed[test_part=="comments"]/60000)
length(unique(forfilterData$ProlificID))
#write.csv(forfilterData,'forfilterData.csv')

#### Here I want to change Select to 0 for problematic subjects
levels(forfilterData$attentionCheck)
#forfilterData[,c("Subj","attentionCheck")]
forfilterData$attCheck2Choice=as.factor(forfilterData$attCheck2Choice)
levels(forfilterData$attCheck2Choice)
#forfilterData[,c("Subj","attCheck2Choice")]
levels(forfilterData$attCheck2Text)
#forfilterData[,c("Subj","attCheck2Text")]

rawData$Select = ifelse((rawData$attentionCheck!="To decide between options"),0,rawData$Select)
rawData$Select = ifelse(is.na(rawData$attCheck2Choice),rawData$Select,0)
rawData$Select[rawData$attCheck2Text==''] = 0

# Subjects who gave problematic answers to comments have to be excluded manually,
#after reading their answers
forfilterData[,c("Subj","comments")]
# e.g., rawData$Select[rawData$Subj==0]=0

rawData$Select=as.factor(rawData$Select)

# Subseting out subjects who failed the attention check or are suspected bots:
rawDataClean = subset(rawData, Select==1)
length(unique(rawDataClean$ProlificID))
#write.csv(rawDataClean,'rawDataClean.csv')

# the IDs of the participants I left out
unique(rawData$ProlificID[rawData$Select == 0])
unique(rawData$Subj[rawData$Select == 0])

#Completion time----
completionTimeClean = subset(rawDataClean,trial_type=="send-data")
completionTimeClean$minutes=completionTimeClean$time_elapsed/60000
mean(completionTimeClean$minutes)
median(completionTimeClean$minutes)
min(completionTimeClean$minutes)
max(completionTimeClean$minutes)

# Demographic Data for the participants we are left with----
demographicDataClean = ddply(rawDataClean, c("Subj","ProlificID","Gender","Age"), summarise,
                             minutes=time_elapsed[test_part=="comments"]/60000)
length(unique(demographicDataClean$ProlificID))
(100*count(demographicDataClean$Gender=="Female")/length(demographicDataClean$Gender))[2,2]
mean(demographicDataClean$Age)
sd(demographicDataClean$Age)

# A dataset of all general questions
subjData = ddply(rawData, c("Subj","ProlificID","Gender","Age",
                            "attentionCheck","attCheck2Choice","attCheck2Text",
                            "comments","Select"), summarise,
                 minutes=time_elapsed[test_part=="comments"]/60000)
#write.csv(subjData,'subjData.csv')
# Subseting out subjects who failed the attention check or are suspected bots:
subjDataClean = subset(subjData, Select==1)
length(unique(subjDataClean$ProlificID))

# Analyze Choice----
choiceTrials = subset(rawDataClean,test_part=="trial")
choiceTrialsWithFlips = read.csv(file="all_subjects.csv", header=T)
choiceTrialsToMerge = choiceTrialsWithFlips[,c("ProlificID","trial_num","flips","max_deviation","middle_crosses")]
choiceTrials = merge(x=choiceTrials,y=choiceTrialsToMerge, by=c("ProlificID", "trial_num"))

hist(choiceTrials$flips, breaks=100)

# labeling for gratton
#re-order the choiceTrials dataset for the gratton labeling
choiceTrials=choiceTrials[order(choiceTrials[,"Subj"], choiceTrials[,"trial_num"]),] 
Previous_Conflict = c(NA,choiceTrials$Conflict)
Previous_Conflict = as.factor(Previous_Conflict)

Previous_Conflict = Previous_Conflict[-length(Previous_Conflict)]
choiceTrials$Previous_Conflict=Previous_Conflict

choiceTrials$Previous_Conflict = ifelse(choiceTrials$trial_num==0,NA,choiceTrials$Previous_Conflict)

choiceTrials$Previous_Conflict = mapvalues(choiceTrials$Previous_Conflict, from = c(1,2),
                                           to = c("AP-AP","AV-AV"))

choiceTrials$taskSwitch = NA
choiceTrials$taskSwitch[choiceTrials$Conflict=="Approach" &
                          choiceTrials$Previous_Conflict=="AP-AP"
] = "Repeat"
choiceTrials$taskSwitch[choiceTrials$Conflict=="Avoidance" &
                          choiceTrials$Previous_Conflict=="AV-AV"
] = "Repeat"
choiceTrials$taskSwitch[choiceTrials$Conflict=="Avoidance" &
                          choiceTrials$Previous_Conflict=="AP-AP"
] = "Switch"
choiceTrials$taskSwitch[choiceTrials$Conflict=="Approach" &
                          choiceTrials$Previous_Conflict=="AV-AV"
] = "Switch"

#write.csv(choiceTrials,'choiceTrialsFromRawDataClean.csv')

# Hist of all trials:
hist(choiceTrials$RT, breaks=10000, main="All Choice Trials",xlab="RT")

hist(choiceTrials$RT, breaks=1000,xlim=c(0,10000), main="All Choice Trials until 10000ms",xlab="RT")

hist(choiceTrials$RT, breaks=1000,xlim=c(0,6000), main="All Choice Trials until 6000ms",xlab="RT")

hist(choiceTrials$RT, breaks=1000,xlim=c(0,4000), main="All Choice Trials until 4000ms",xlab="RT")

hist(choiceTrials$RT,  breaks=2000,main="All Choice Trials until 300ms",xlim=c(0,300),xlab="RT")

# Subsetting trials faster than 200ms:
choiceTrialsClean=subset(choiceTrials, RT>200)
100*(1-length(choiceTrialsClean$RT)/length(choiceTrials$RT))
min(choiceTrials$RT)

# datasets in which I clean the RT according to the distribution cut-off
choiceTrialsClean4000=subset(choiceTrials, RT<4000)

choiceTrialsClean$logRT=log(choiceTrialsClean$RT)
hist(choiceTrialsClean$logRT, breaks=100, main="All Choice Trials log transformed",xlab="log RT")


choice.Subj = ddply(choiceTrialsClean, "Subj", summarise,
                    meanRT = mean(RT, na.rm = T),
                    sdRT   = sd(RT, na.rm = T) )

choice.Subj$ZmeanRT = (choice.Subj$meanRT - mean(choice.Subj$meanRT))/sd(choice.Subj$meanRT)

# A 1 or 0 variable
choice.Subj$outlier.Subj = ifelse((choice.Subj$ZmeanRT < -3) |  (choice.Subj$ZmeanRT > 3),1,0)

choice.Subj$outlier.Subj=as.factor(choice.Subj$outlier.Subj)
levels(choice.Subj$outlier.Subj)
choice.Subj[,c("Subj","outlier.Subj")]
choice.Subj$Subj[choice.Subj$outlier.Subj == 1] #which Ss are outliers

rawDataCleaner = merge(rawDataClean,choice.Subj)
rawDataCleaner = subset(rawDataCleaner,outlier.Subj==0)
# Demographic Data for the participants we are left with w/o outlierSubjs----
demographicDataCleaner = ddply(rawDataCleaner, c("Subj","ProlificID","Gender","Age"), summarise,
                               minutes=time_elapsed[test_part=="comments"]/60000)
length(unique(demographicDataCleaner$ProlificID))
(100*count(demographicDataCleaner$Gender=="Female")/length(demographicDataCleaner$Gender))[2,2]
mean(demographicDataCleaner$Age)
sd(demographicDataCleaner$Age)


choiceTrialsClean = merge(choiceTrialsClean,choice.Subj)
#summary(choiceTrialsClean$Conflict)
choiceTrialsClean=droplevels.data.frame(choiceTrialsClean)
choiceTrialsClean$Conflict=as.factor(choiceTrialsClean$Conflict)
levels(choiceTrialsClean$Conflict)=c("AP-AP","AV-AV")
choiceTrialsClean.almost.er=subset(choiceTrialsClean, outlier.Subj==0)
#write.csv(choiceTrialsClean.almost.er,'choiceTrialsClean.almost.er.csv')
100*(1-length(choiceTrialsClean.almost.er$RT)/length(choiceTrialsClean$RT))
sum(choice.Subj$outlier.Subj==1)
length(unique(choiceTrialsClean.almost.er$ProlificID))

choiceTrialsClean.almost.er$ZRT = (choiceTrialsClean.almost.er$RT - choiceTrialsClean.almost.er$meanRT)/choiceTrialsClean.almost.er$sdRT

# A 1 or 0 variable
choiceTrialsClean.almost.er$outlier.Trial = ifelse((choiceTrialsClean.almost.er$ZRT > -3) & (choiceTrialsClean.almost.er$ZRT < 3), 0, 1)

choiceTrialsCleaner=subset(choiceTrialsClean.almost.er, outlier.Trial==0)
100*(1-length(choiceTrialsCleaner$RT)/length(choiceTrialsClean.almost.er$RT))
#summary(choiceTrialsCleaner)

# Exmaining Before and after Histograms:
hist(choiceTrials$RT, breaks=100, main="All Choice Trials",xlab="RT")
hist(choiceTrialsCleaner$RT, breaks=100, main="Only RTs above 200 and no outliers",xlab="RT")

choiceTrialsCleaner$logRT=log(choiceTrialsCleaner$RT)
hist(choiceTrialsCleaner$logRT, breaks=100, main="Choice Trials (w/o 3 SDs) log transformed",xlab="log RT")

# Drop levels
choiceTrials=droplevels.data.frame(choiceTrials)
choiceTrialsClean=droplevels.data.frame(choiceTrialsClean)
choiceTrialsCleaner=droplevels.data.frame(choiceTrialsCleaner)
subjDataClean=droplevels.data.frame(subjDataClean)
choiceTrialsClean4000=droplevels.data.frame(choiceTrialsClean4000)

hist(choiceTrialsCleaner$RT, breaks=100, main="Only RTs above 200 and no outliers",xlab="RT")
max(choiceTrialsCleaner$RT)

#percentages of trials subsetted
100*(1-length(choiceTrialsClean$RT)/length(choiceTrials$RT))
100*(1-length(choiceTrialsCleaner$RT)/length(choiceTrials$RT))
100*(1-length(choiceTrialsClean4000$RT)/length(choiceTrials$RT))

## Aggregating data:
# calculate the mean and SD of RTs for each participant in each condition
# Analyze RT----
RT.data.c = ddply(choiceTrialsCleaner, c("Subj","Conflict"), summarise,
                  meanRT = mean(RT, na.rm = T),
                  sdRT = sd(RT, na.rm = T))

RT.wide = dcast(RT.data.c, Subj ~ Conflict, value.var = "meanRT")
RT.wide$meanPerSubject = apply(RT.wide[,2:3], 1, mean)
generalMean = mean(RT.wide$meanPerSubject)
generalMean
sd(RT.wide$meanPerSubject)

RT.subjects=merge(RT.data.c,RT.wide[,c("Subj","meanPerSubject")])

RT.subjects$standardizedMeanRT = RT.subjects$meanRT - RT.subjects$meanPerSubject + generalMean # Following Cousineau 2005 Tutorials in Quantitative Methods for Psychology 

n.cells = 2
cf = sqrt(n.cells/(n.cells-1)) # Following Morey 2008 in Tutorials in Quantitative Methods for Psychology,
# the correction factor is sqrt(number of overall cells/number of overall cells-1)

RT.groups.c = ddply(RT.subjects, c("Conflict"), summarise,
                    mean = mean(meanRT, na.rm = T),
                    sd = sd(meanRT, na.rm=T),
                    n=length(unique(Subj)),
                    sdForErrorBars = sd(standardizedMeanRT, na.rm=T),
                    seForErrorBars.beforeMoreyCorrection=sdForErrorBars/sqrt(n),
                    seForErrorBars = seForErrorBars.beforeMoreyCorrection*cf,
                    CIRT = 1.96*seForErrorBars) #95% Confidence interval

RT.groups.c

ddply(RT.subjects, c("Conflict"), summarise,
      mean = mean(meanRT, na.rm = T),
      sd = sd(meanRT, na.rm=T))

t.test(meanRT ~ Conflict, data=RT.data.c,paired=T)
cohensD(meanRT ~ Conflict, data=RT.data.c,method="paired")

#Graph
ggplot(RT.groups.c, aes(x=Conflict, y=mean, fill=Conflict)) +
  geom_bar(width=0.8, position=position_dodge(.9), colour="black", stat="identity") +
  geom_errorbar(position=position_dodge(.9), width=.2, aes(ymin=mean-seForErrorBars, ymax=mean+seForErrorBars)) +
  scale_fill_manual(values=c("#336600", "#990033")) + 
  theme_minimal()  +
  ggtitle("RT") + 
  theme(plot.title = element_text(hjust = 0.5)) +
  ylab("RT") +
  xlab("Conflict") + 
  guides(fill=guide_legend(title="Conflict")) +
  coord_cartesian(ylim=c(1900,2400))
#ggsave("RT.png",width=5,height=5)

# violin plot
ggplot(RT.data.c, aes(x=Conflict, y=meanRT, color=Conflict)) +
  geom_violin()+ 
  theme_classic()  +
  ggtitle("RT")  +
  ylab("RT (ms)") +
  xlab("Conflict") + 
  theme(plot.title = element_text(hjust = 0.5)) +
  theme(text = element_text(size=15))+ 
  #geom_dotplot(binaxis='y', stackdir='center', dotsize=1)
  geom_boxplot(width=0.1) +
  scale_color_manual(values=c("#336600", "#990033"))
#ggsave("RTViolinPlot.png",width=5,height=5)

#flips----
flips.data.c = ddply(choiceTrialsCleaner, c("Subj","Conflict"), summarise,
                          meanFlips = mean(flips, na.rm = T),
                          sdFlips = sd(flips, na.rm = T))

ddply(flips.data.c, c("Conflict"), summarise,
      meanFlip = mean(meanFlips, na.rm = T),
      sdFlip = sd(meanFlips, na.rm = T))
t.test(meanFlips ~ Conflict, data = flips.data.c,paired=TRUE)
cohensD(meanFlips ~ Conflict, data = flips.data.c,method="paired")


flips.wide = dcast(flips.data.c, Subj ~ Conflict, value.var = "meanFlips")
flips.wide$meanPerSubject = apply(flips.wide[,2:3], 1, mean)
generalMean.flips = mean(flips.wide$meanPerSubject)
generalMean.flips
sd(flips.wide$meanPerSubject)

flips.subjects=merge(flips.data.c,flips.wide[,c("Subj","meanPerSubject")])

flips.subjects$standardizedmeanFlips = flips.subjects$meanFlips - flips.subjects$meanPerSubject + generalMean.flips # Following Cousineau 2005 Tutorials in Quantitative Methods for Psychology 

n.cells = 2
cf = sqrt(n.cells/(n.cells-1)) # Following Morey 2008 in Tutorials in Quantitative Methods for Psychology,
# the correction factor is sqrt(number of overall cells/number of overall cells-1)

flips.groups.c = ddply(flips.subjects, c("Conflict"), summarise,
                            mean = mean(meanFlips, na.rm = T),
                            sd = sd(meanFlips, na.rm=T),
                            n=length(unique(Subj)),
                            sdForErrorBars = sd(standardizedmeanFlips, na.rm=T),
                            seForErrorBars.beforeMoreyCorrection=sdForErrorBars/sqrt(n),
                            seForErrorBars = seForErrorBars.beforeMoreyCorrection*cf,
                            CIRT = 1.96*seForErrorBars) #95% Confidence interval

flips.groups.c

#Graph
ggplot(flips.groups.c, aes(x=Conflict, y=mean, fill=Conflict)) +
  geom_bar(width=0.8, position=position_dodge(.9), colour="black", stat="identity") +
  geom_errorbar(position=position_dodge(.9), width=.2, aes(ymin=mean-seForErrorBars, ymax=mean+seForErrorBars)) +
  scale_fill_manual(values=c("#336600", "#990033")) + 
  theme_minimal()  +
  ggtitle("X-flips") + 
  theme(plot.title = element_text(hjust = 0.5)) +
  ylab("X-flips") +
  xlab("Conflict") + 
  guides(fill=guide_legend(title="Conflict")) +
  coord_cartesian(ylim=c(2.3,3.3))
#ggsave("flips.png",width=5,height=5)

# violin plot
ggplot(flips.data.c, aes(x=Conflict, y=meanFlips, color=Conflict)) +
  geom_violin()+ 
  theme_classic()  +
  ggtitle("X-Flips")  +
  ylab("Mean X-Flips") +
  xlab("Conflict") + 
  theme(plot.title = element_text(hjust = 0.5)) +
  theme(text = element_text(size=15))+ 
  #geom_dotplot(binaxis='y', stackdir='center', dotsize=1)
  geom_boxplot(width=0.1) +
  scale_color_manual(values=c("#336600", "#990033"))
#ggsave("FlipsViolinPlot.png",width=5,height=5)

#flips on all trials----
flips.data.conflict.all = ddply(choiceTrials, c("Subj","Conflict"), summarise,
                                 meanFlips = mean(flips, na.rm = T),
                                 sdFlips = sd(flips, na.rm = T))
flips.data.conflict.all$Conflict =as.factor(flips.data.conflict.all$Conflict)
levels(flips.data.conflict.all$Conflict) = c("AP-AP","AV-AV")
ddply(flips.data.conflict.all, c("Conflict"), summarise,
      meanFlip = mean(meanFlips, na.rm = T),
      sdFlip = sd(meanFlips, na.rm = T))
t.test(meanFlips ~ Conflict, data = flips.data.conflict.all,paired=TRUE)
cohensD(meanFlips ~ Conflict, data = flips.data.conflict.all,method="paired")


flips.wide.all = dcast(flips.data.conflict.all, Subj ~ Conflict, value.var = "meanFlips")
flips.wide.all$meanPerSubject = apply(flips.wide.all[,2:3], 1, mean)
generalMean.flips.all = mean(flips.wide.all$meanPerSubject)
generalMean.flips.all
sd(flips.wide.all$meanPerSubject)

flips.subjects.all=merge(flips.data.conflict.all,flips.wide.all[,c("Subj","meanPerSubject")])

flips.subjects.all$standardizedmeanFlips = flips.subjects.all$meanFlips - flips.subjects.all$meanPerSubject + generalMean.flips.all # Following Cousineau 2005 Tutorials in Quantitative Methods for Psychology 

n.cells = 2
cf = sqrt(n.cells/(n.cells-1)) # Following Morey 2008 in Tutorials in Quantitative Methods for Psychology,
# the correction factor is sqrt(number of overall cells/number of overall cells-1)

flips.groups = ddply(flips.subjects.all, c("Conflict"), summarise,
                            mean = mean(meanFlips, na.rm = T),
                            sd = sd(meanFlips, na.rm=T),
                            n=length(unique(Subj)),
                            sdForErrorBars = sd(standardizedmeanFlips, na.rm=T),
                            seForErrorBars.beforeMoreyCorrection=sdForErrorBars/sqrt(n),
                            seForErrorBars = seForErrorBars.beforeMoreyCorrection*cf,
                            CIRT = 1.96*seForErrorBars) #95% Confidence interval

flips.groups

#Graph
ggplot(flips.groups, aes(x=Conflict, y=mean, fill=Conflict)) +
  geom_bar(width=0.8, position=position_dodge(.9), colour="black", stat="identity") +
  geom_errorbar(position=position_dodge(.9), width=.2, aes(ymin=mean-seForErrorBars, ymax=mean+seForErrorBars)) +
  scale_fill_manual(values=c("#336600", "#990033")) + 
  theme_minimal()  +
  ggtitle("x-flips") + 
  theme(plot.title = element_text(hjust = 0.5)) +
  ylab("x-flips") +
  xlab("Conflict") + 
  guides(fill=guide_legend(title="Conflict")) +
  coord_cartesian(ylim=c(2.3,3.3))
#ggsave("flipsOnAllTrials.png",width=5,height=5)

# violin plot
ggplot(flips.data.conflict.all, aes(x=Conflict, y=meanFlips, color=Conflict)) +
  geom_violin()+ 
  theme_classic()  +
  ggtitle("X-Flips (on all trials)")  +
  ylab("Mean X-Flips") +
  xlab("Conflict") + 
  theme(plot.title = element_text(hjust = 0.5)) +
  theme(text = element_text(size=15))+ 
  #geom_dotplot(binaxis='y', stackdir='center', dotsize=1)
  geom_boxplot(width=0.1) +
  scale_color_manual(values=c("#336600", "#990033"))
#ggsave("FlipsForAllTrialsViolinPlot.png",width=5,height=5)

#MD----
hist(choiceTrialsCleaner$max_deviation)
hist(choiceTrialsCleaner$max_deviation, breaks=100, main="Maximum Deviation",xlab="MD")
hist(choiceTrialsClean$max_deviation)
choiceTrialsCleaner.ap=subset(choiceTrialsCleaner,Conflict=="AP-AP")
choiceTrialsCleaner.av=subset(choiceTrialsCleaner,Conflict=="AV-AV")
hist(choiceTrialsCleaner.ap$max_deviation, breaks=100, main="Maximum Deviation for AP-AP",xlab="MD")
hist(choiceTrialsCleaner.av$max_deviation, breaks=100, main="Maximum Deviation for AV-AV",xlab="MD")
MD.data.c = ddply(choiceTrialsCleaner, c("Subj","Conflict"), summarise,
                  meanMD = mean(max_deviation, na.rm = T),
                  sdMD = sd(max_deviation, na.rm = T))
hist(MD.data.c$meanMD)
ddply(MD.data.c, c("Conflict"), summarise,
      meanMaxDeviation = mean(meanMD, na.rm = T),
      sdMaxDeviation = sd(meanMD, na.rm = T))
t.test(meanMD ~ Conflict, data = MD.data.c,paired=TRUE)
cohensD(meanMD ~ Conflict, data = MD.data.c,method="paired")


MD.wide = dcast(MD.data.c, Subj ~ Conflict, value.var = "meanMD")
MD.wide$meanPerSubject = apply(MD.wide[,2:3], 1, mean)
generalMean.MD = mean(MD.wide$meanPerSubject)
generalMean.MD
sd(MD.wide$meanPerSubject)

MD.subjects=merge(MD.data.c,MD.wide[,c("Subj","meanPerSubject")])

MD.subjects$standardizedmeanMD = MD.subjects$meanMD - MD.subjects$meanPerSubject + generalMean.MD # Following Cousineau 2005 Tutorials in Quantitative Methods for Psychology 

n.cells = 2
cf = sqrt(n.cells/(n.cells-1)) # Following Morey 2008 in Tutorials in Quantitative Methods for Psychology,
# the correction factor is sqrt(number of overall cells/number of overall cells-1)

MD.groups.c = ddply(MD.subjects, c("Conflict"), summarise,
                    mean = mean(meanMD, na.rm = T),
                    sd = sd(meanMD, na.rm=T),
                    n=length(unique(Subj)),
                    sdForErrorBars = sd(standardizedmeanMD, na.rm=T),
                    seForErrorBars.beforeMoreyCorrection=sdForErrorBars/sqrt(n),
                    seForErrorBars = seForErrorBars.beforeMoreyCorrection*cf,
                    CIRT = 1.96*seForErrorBars) #95% Confidence interval

MD.groups.c

#Graph
ggplot(MD.groups.c, aes(x=Conflict, y=mean, fill=Conflict)) +
  geom_bar(width=0.8, position=position_dodge(.9), colour="black", stat="identity") +
  geom_errorbar(position=position_dodge(.9), width=.2, aes(ymin=mean-seForErrorBars, ymax=mean+seForErrorBars)) +
  scale_fill_manual(values=c("#336600", "#990033")) + 
  theme_minimal()  +
  ggtitle("MD") + 
  theme(plot.title = element_text(hjust = 0.5)) +
  ylab("MD") +
  xlab("Conflict") + 
  guides(fill=guide_legend(title="Conflict")) +
  coord_cartesian(ylim=c(0.7,0.95))
#ggsave("MD.png",width=5,height=5)

# violin plot
ggplot(MD.data.c, aes(x=Conflict, y=meanMD, color=Conflict)) +
  geom_violin()+ 
  theme_classic()  +
  ggtitle("MD")  +
  ylab("Mean MD") +
  xlab("Conflict") + 
  theme(plot.title = element_text(hjust = 0.5)) +
  theme(text = element_text(size=15))+ 
  #geom_dotplot(binaxis='y', stackdir='center', dotsize=1)
  geom_boxplot(width=0.1) +
  scale_color_manual(values=c("#336600", "#990033"))
#ggsave("MDViolinPlot.png",width=5,height=5)

#Middle Crosses----
MC.data.c = ddply(choiceTrialsCleaner, c("Subj","Conflict"), summarise,
                  meanMC = mean(middle_crosses, na.rm = T),
                  sdMC = sd(middle_crosses, na.rm = T))
ddply(MC.data.c, c("Conflict"), summarise,
      meanMiddleCrosses = mean(meanMC, na.rm = T),
      sdMiddleCrosses = sd(meanMC, na.rm = T))
t.test(meanMC ~ Conflict, data = MC.data.c,paired=TRUE)
cohensD(meanMC ~ Conflict, data = MC.data.c,method="paired")


MC.wide = dcast(MC.data.c, Subj ~ Conflict, value.var = "meanMC")
MC.wide$meanPerSubject = apply(MC.wide[,2:3], 1, mean)
generalMean.MC = mean(MC.wide$meanPerSubject)
generalMean.MC
sd(MC.wide$meanPerSubject)

MC.subjects=merge(MC.data.c,MC.wide[,c("Subj","meanPerSubject")])

MC.subjects$standardizedmeanMC = MC.subjects$meanMC - MC.subjects$meanPerSubject + generalMean.MC # Following Cousineau 2005 Tutorials in Quantitative Methods for Psychology 

n.cells = 2
cf = sqrt(n.cells/(n.cells-1)) # Following Morey 2008 in Tutorials in Quantitative Methods for Psychology,
# the correction factor is sqrt(number of overall cells/number of overall cells-1)

MC.groups.c = ddply(MC.subjects, c("Conflict"), summarise,
                    mean = mean(meanMC, na.rm = T),
                    sd = sd(meanMC, na.rm=T),
                    n=length(unique(Subj)),
                    sdForErrorBars = sd(standardizedmeanMC, na.rm=T),
                    seForErrorBars.beforeMoreyCorrection=sdForErrorBars/sqrt(n),
                    seForErrorBars = seForErrorBars.beforeMoreyCorrection*cf,
                    CIRT = 1.96*seForErrorBars) #95% Confidence interval

MC.groups.c

#Graph
ggplot(MC.groups.c, aes(x=Conflict, y=mean, fill=Conflict)) +
  geom_bar(width=0.8, position=position_dodge(.9), colour="black", stat="identity") +
  geom_errorbar(position=position_dodge(.9), width=.2, aes(ymin=mean-seForErrorBars, ymax=mean+seForErrorBars)) +
  scale_fill_manual(values=c("#336600", "#990033")) + 
  theme_minimal()  +
  ggtitle("MC") + 
  theme(plot.title = element_text(hjust = 0.5)) +
  ylab("MC") +
  xlab("Conflict") + 
  guides(fill=guide_legend(title="Conflict")) +
  coord_cartesian(ylim=c(1.3,2))
#ggsave("MC.png",width=5,height=5)

# violin plot
ggplot(MC.data.c, aes(x=Conflict, y=meanMC, color=Conflict)) +
  geom_violin()+ 
  theme_classic()  +
  ggtitle("MC")  +
  ylab("Mean MC") +
  xlab("Conflict") + 
  theme(plot.title = element_text(hjust = 0.5)) +
  theme(text = element_text(size=15))+ 
  #geom_dotplot(binaxis='y', stackdir='center', dotsize=1)
  geom_boxplot(width=0.1) +
  scale_color_manual(values=c("#336600", "#990033"))
#ggsave("MCViolinPlot.png",width=5,height=5)

#first movement time----
# first clean the first_movement_time trials as well
choiceTrialsCleanerAlsoForInitialRT = choiceTrialsCleaner

choice.Subj.initialRT = ddply(choiceTrialsCleanerAlsoForInitialRT, "Subj", summarise,
                              meaninitialRT = mean(first_movement_time, na.rm = T),
                              sdinitialRT = sd(first_movement_time, na.rm = T) )

choice.Subj.initialRT$ZmeaninitialRT = (choice.Subj.initialRT$meaninitialRT - mean(choice.Subj.initialRT$meaninitialRT))/sd(choice.Subj.initialRT$meaninitialRT)

choice.Subj.initialRT$outlier.SubjinitialRT = ifelse((choice.Subj.initialRT$ZmeaninitialRT < -3) |  (choice.Subj.initialRT$ZmeaninitialRT > 3),1,0)

choice.Subj.initialRT$outlier.SubjinitialRT=as.factor(choice.Subj.initialRT$outlier.SubjinitialRT)
levels(choice.Subj.initialRT$outlier.SubjinitialRT)
choice.Subj.initialRT[,c("Subj","outlier.SubjinitialRT")]
#No Ss are outliers

choiceTrialsCleanerAlsoForInitialRT = merge(choiceTrialsCleanerAlsoForInitialRT,choice.Subj.initialRT)

choiceTrialsandinitialRTClean.almost.er=subset(choiceTrialsCleanerAlsoForInitialRT, outlier.SubjinitialRT==0)
100*(1-length(choiceTrialsandinitialRTClean.almost.er$RT)/length(choiceTrialsCleanerAlsoForInitialRT$RT))
sum(choice.Subj.initialRT$outlier.SubjinitialRT==1)
length(unique(choiceTrialsandinitialRTClean.almost.er$ProlificID))

choiceTrialsandinitialRTClean.almost.er$ZinitialRT = (choiceTrialsandinitialRTClean.almost.er$first_movement_time - choiceTrialsandinitialRTClean.almost.er$meaninitialRT)/choiceTrialsandinitialRTClean.almost.er$sdinitialRT

choiceTrialsandinitialRTClean.almost.er$outlier.initialRTTrial = ifelse((choiceTrialsandinitialRTClean.almost.er$ZinitialRT > -3) & (choiceTrialsandinitialRTClean.almost.er$ZinitialRT < 3), 0, 1)

choiceTrialsandinitialRTCleaner=subset(choiceTrialsandinitialRTClean.almost.er, outlier.initialRTTrial==0)
100*(1-length(choiceTrialsandinitialRTCleaner$RT)/length(choiceTrialsandinitialRTClean.almost.er$RT))

hist(choiceTrialsCleanerAlsoForInitialRT$first_movement_time, breaks=100, main="All Trials cleaned only by choice RT",xlab="flips RT")
hist(choiceTrialsandinitialRTCleaner$first_movement_time, breaks=100, main="Only initial RTs above 200 and no outliers",xlab="flips RT")
hist(choiceTrialsandinitialRTCleaner$first_movement_time, breaks=100, main="Only initial RTs above 200 and below 1000",xlim=c(0,1000),xlab="flips RT")

choiceTrialsCleanerAlsoForInitialRT=droplevels.data.frame(choiceTrialsCleanerAlsoForInitialRT)
choiceTrialsandinitialRTCleaner=droplevels.data.frame(choiceTrialsandinitialRTCleaner)

initial.RT.data.c = ddply(choiceTrialsandinitialRTCleaner, c("Subj","Conflict"), summarise,
                          meanInitialRT = mean(first_movement_time, na.rm = T),
                          sdInitialRT = sd(first_movement_time, na.rm = T))

initial.RT.wide = dcast(initial.RT.data.c, Subj ~ Conflict, value.var = "meanInitialRT")
initial.RT.wide$meanPerSubject = apply(initial.RT.wide[,2:3], 1, mean)
generalMean.initial = mean(initial.RT.wide$meanPerSubject)
generalMean.initial
sd(initial.RT.wide$meanPerSubject)

initial.RT.subjects=merge(initial.RT.data.c,initial.RT.wide[,c("Subj","meanPerSubject")])

initial.RT.subjects$standardizedMeanRT = initial.RT.subjects$meanInitialRT - initial.RT.subjects$meanPerSubject + generalMean.initial # Following Cousineau 2005 Tutorials in Quantitative Methods for Psychology 

n.cells = 2
cf = sqrt(n.cells/(n.cells-1)) # Following Morey 2008 in Tutorials in Quantitative Methods for Psychology,
# the correction factor is sqrt(number of overall cells/number of overall cells-1)

initial.RT.groups.c = ddply(initial.RT.subjects, c("Conflict"), summarise,
                            mean = mean(meanInitialRT, na.rm = T),
                            sd = sd(meanInitialRT, na.rm=T),
                            n=length(unique(Subj)),
                            sdForErrorBars = sd(standardizedMeanRT, na.rm=T),
                            seForErrorBars.beforeMoreyCorrection=sdForErrorBars/sqrt(n),
                            seForErrorBars = seForErrorBars.beforeMoreyCorrection*cf,
                            CIRT = 1.96*seForErrorBars) #95% Confidence interval

initial.RT.groups.c

ddply(initial.RT.subjects, c("Conflict"), summarise,
      mean = mean(meanInitialRT, na.rm = T),
      sd = sd(meanInitialRT, na.rm=T))

t.test(meanInitialRT ~ Conflict, data=initial.RT.data.c,paired=T)
cohensD(meanInitialRT ~ Conflict, data=initial.RT.data.c,method="paired")

#Graph
ggplot(initial.RT.groups.c, aes(x=Conflict, y=mean, fill=Conflict)) +
  geom_bar(width=0.8, position=position_dodge(.9), colour="black", stat="identity") +
  geom_errorbar(position=position_dodge(.9), width=.2, aes(ymin=mean-seForErrorBars, ymax=mean+seForErrorBars)) +
  scale_fill_manual(values=c("#336600", "#990033")) + 
  theme_minimal()  +
  ggtitle("RT for First movement") + 
  theme(plot.title = element_text(hjust = 0.5)) +
  ylab("RT for First movement (ms)") +
  xlab("Conflict") + 
  guides(fill=guide_legend(title="Conflict")) +
  coord_cartesian(ylim=c(350,380))
#ggsave("RT.png",width=5,height=5)

# violin plot
ggplot(initial.RT.data.c, aes(x=Conflict, y=meanInitialRT, color=Conflict)) +
  geom_violin()+ 
  theme_classic()  +
  ggtitle("RT for First movement")  +
  ylab("RT for First movement (ms)") +
  xlab("Conflict") + 
  theme(plot.title = element_text(hjust = 0.5)) +
  theme(text = element_text(size=13))+ 
  #geom_dotplot(binaxis='y', stackdir='center', dotsize=1)
  geom_boxplot(width=0.1) +
  scale_color_manual(values=c("#336600", "#990033"))
#ggsave("RTViolinPlot.png",width=5,height=5)

# intransitivity----
intransitivity=read.csv(file="intransitivity.csv", header=T)
excludedSubjs=unique(rawData$Subj[rawData$Select==0])
intransitivityClean = intransitivity[!intransitivity$Subj %in% excludedSubjs, ]

transitivity.by.condition = ddply(intransitivityClean, c("Conflict"), summarise,
                                  mean = mean(intransitivity, na.rm = T),
                                  sd = sd(intransitivity, na.rm=T),
                                  n=length(unique(Subj)))

transitivity.by.condition
t.test(intransitivity ~ Conflict, data = intransitivityClean,paired=T)
cohensD(intransitivity ~ Conflict, data = intransitivityClean,method="paired")

# violin plot
ggplot(intransitivityClean, aes(x=Conflict, y=intransitivity, color=Conflict)) +
  geom_violin()+ 
  theme_classic()  +
  ggtitle("Transitivity violations")  +
  ylab("Intransitivity") +
  xlab("Conflict") + 
  theme(plot.title = element_text(hjust = 0.5)) +
  theme(text = element_text(size=15))+ 
  #geom_dotplot(binaxis='y', stackdir='center', dotsize=1)
  geom_boxplot(width=0.1) +
  scale_color_manual(values=c("#336600", "#990033"))
#ggsave("IntransitivityViolinPlot.png",width=5,height=5)

# correlations----
choiceTrialsCleanerAlsoForInitialRTWithIntransitivity=merge(choiceTrialsCleanerAlsoForInitialRT,intransitivityClean)
cor.data = ddply(choiceTrialsCleanerAlsoForInitialRTWithIntransitivity, c("Subj","Conflict"), summarise,
                     meanRT = mean(RT, na.rm = T),
                     meanInitialRT = mean(first_movement_time, na.rm = T),
                     meanMD=mean(max_deviation, na.rm = T),
                     meanFlips=mean(flips, na.rm = T),
                     meanMiddleCrosses = mean(middle_crosses, na.rm = T),
                     Intransitivity = mean(intransitivity, na.rm = T))
#write.csv(cor.data,"corDataAllMeasures.csv")

cor.data.app = subset(cor.data,Conflict=="AP-AP")
cor.data.avo = subset(cor.data,Conflict=="AV-AV")

apa.cor.table(subset(cor.data, select = c(meanRT,meanInitialRT,meanMD,meanFlips,meanMiddleCrosses,Intransitivity)))
#apa.cor.table(subset(cor.data, select = c(meanRT,meanInitialRT,meanMD,meanFlips,meanMiddleCrosses,Intransitivity)), 
#              filename = "apaCorTable.doc")


apa.cor.table(subset(cor.data.app, select = c(meanRT,meanInitialRT,meanMD,meanFlips,meanMiddleCrosses,Intransitivity)))
#apa.cor.table(subset(cor.data.app, select = c(meanRT,meanInitialRT,meanMD,meanFlips,meanMiddleCrosses,Intransitivity)), 
#              filename = "apaCorTableAP.doc")

apa.cor.table(subset(cor.data.avo, select = c(meanRT,meanInitialRT,meanMD,meanFlips,meanMiddleCrosses,Intransitivity)))
#apa.cor.table(subset(cor.data.avo, select = c(meanRT,meanInitialRT,meanMD,meanFlips,meanMiddleCrosses,Intransitivity)), 
#              filename = "apaCorTableAV.doc")

# Regression analysis on RT----
contrasts(choiceTrialsCleaner$Conflict)=matrix(c(-1,1), nrow = 2, byrow=T)
contrasts(choiceTrialsCleaner$Conflict)

mixed.model.RT = lmer(RT ~ Conflict + 
                          (1|Subj),
                        data = choiceTrialsCleaner)
summary(mixed.model.RT)

# LRT for Conflict
mixed.model.RT.compConflict = lmer(RT ~
                                     (1|Subj),
                                   data = choiceTrialsCleaner)
anova(mixed.model.RT, mixed.model.RT.compConflict)

# Regression analysis on initial RT----
contrasts(choiceTrialsCleaner$Conflict)=matrix(c(-1,1), nrow = 2, byrow=T)
contrasts(choiceTrialsCleaner$Conflict)

mixed.model.initial.RT = lmer(first_movement_time ~ Conflict + 
                        (1|Subj),
                      data = choiceTrialsCleaner)
summary(mixed.model.initial.RT)

# LRT for Conflict
mixed.model.initial.RT.compConflict = lmer(first_movement_time ~
                                     (1|Subj),
                                   data = choiceTrialsCleaner)
anova(mixed.model.initial.RT, mixed.model.initial.RT.compConflict)

# Regression flips----
mixed.model.flips = lmer(flips ~ Conflict + 
                          (1|Subj),
                        data = choiceTrialsCleaner)
summary(mixed.model.flips)

# LRT for Conflict
mixed.model.flips.compConflict = lmer(flips ~ 
                                       (1|Subj),
                                     data = choiceTrialsCleaner)
anova(mixed.model.flips, mixed.model.flips.compConflict)

# Regression analysis on MD----
#contrasts(choiceTrialsCleaner$Conflict)=matrix(c(-1,1), nrow = 2, byrow=T)
contrasts(choiceTrialsCleaner$Conflict)

mixed.model.MD = lmer(max_deviation ~ Conflict + 
                        (1|Subj),
                      data = choiceTrialsCleaner)
summary(mixed.model.MD)

# LRT for Conflict
mixed.model.MD.compConflict = lmer(max_deviation ~
                                     (1|Subj),
                                   data = choiceTrialsCleaner)
anova(mixed.model.MD, mixed.model.MD.compConflict)

#regression analysis for MD controlling for RT----
mixed.model.MD.RT = lmer(max_deviation ~ RT + Conflict + 
                        (1|Subj),
                      data = choiceTrialsCleaner)
summary(mixed.model.MD.RT)

# LRT for Conflict
mixed.model.MD.RT.compConflict = lmer(max_deviation ~ RT +
                                     (1|Subj),
                                   data = choiceTrialsCleaner)
anova(mixed.model.MD.RT, mixed.model.MD.RT.compConflict)

# regression analysis for flips - on all trials-----------
length(unique(choiceTrials$Subj))
choiceTrials$Conflict=as.factor(choiceTrials$Conflict)
levels(choiceTrials$Conflict)=c("AP-AP","AV-AV")
contrasts(choiceTrials$Conflict)=matrix(c(-1,1), nrow = 2, byrow=T)
contrasts(choiceTrials$Conflict)
# Regression flips
mixed.model.flips.all = lmer(flips ~ Conflict + 
                          (1|Subj),
                        data = choiceTrials)
summary(mixed.model.flips.all)

# LRT for Conflict
mixed.model.flips.compConflict.all = lmer(flips ~ 
                                       (1|Subj),
                                     data = choiceTrials)
anova(mixed.model.flips.all, mixed.model.flips.compConflict.all)

#results when cleaning RT by 4000ms cutoff----
choiceTrialsClean4000$Conflict=as.factor(choiceTrialsClean4000$Conflict)
levels(choiceTrialsClean4000$Conflict)=c("AP-AP","AV-AV")
RT.data.4000 = ddply(choiceTrialsClean4000, c("Subj","Conflict"), summarise,
                  meanRT = mean(RT, na.rm = T),
                  sdRT = sd(RT, na.rm = T))
RT.wide.4000 = dcast(RT.data.4000, Subj ~ Conflict, value.var = "meanRT")
RT.wide.4000$meanPerSubject = apply(RT.wide.4000[,2:3], 1, mean)
generalMean.4000 = mean(RT.wide.4000$meanPerSubject)
generalMean.4000
sd(RT.wide.4000$meanPerSubject)

RT.subjects.4000=merge(RT.data.4000,RT.wide.4000[,c("Subj","meanPerSubject")])

RT.subjects.4000$standardizedMeanRT = RT.subjects.4000$meanRT - RT.subjects.4000$meanPerSubject + generalMean.4000 # Following Cousineau 2005 Tutorials in Quantitative Methods for Psychology 

n.cells = 2
cf = sqrt(n.cells/(n.cells-1)) # Following Morey 2008 in Tutorials in Quantitative Methods for Psychology,
# the correction factor is sqrt(number of overall cells/number of overall cells-1)

RT.groups.4000 = ddply(RT.subjects.4000, c("Conflict"), summarise,
                    mean = mean(meanRT, na.rm = T),
                    sd = sd(meanRT, na.rm=T),
                    n=length(unique(Subj)),
                    sdForErrorBars = sd(standardizedMeanRT, na.rm=T),
                    seForErrorBars.beforeMoreyCorrection=sdForErrorBars/sqrt(n),
                    seForErrorBars = seForErrorBars.beforeMoreyCorrection*cf,
                    CIRT = 1.96*seForErrorBars) #95% Confidence interval

RT.groups.4000

ddply(RT.subjects.4000, c("Conflict"), summarise,
      mean = mean(meanRT, na.rm = T),
      sd = sd(meanRT, na.rm=T))

t.test(meanRT ~ Conflict, data=RT.data.4000,paired=T)
cohensD(meanRT ~ Conflict, data=RT.data.4000,method="paired")

#Graph
ggplot(RT.groups.4000, aes(x=Conflict, y=mean, fill=Conflict)) +
  geom_bar(width=0.8, position=position_dodge(.9), colour="black", stat="identity") +
  geom_errorbar(position=position_dodge(.9), width=.2, aes(ymin=mean-seForErrorBars, ymax=mean+seForErrorBars)) +
  scale_fill_manual(values=c("#336600", "#990033")) + 
  theme_minimal()  +
  ggtitle("RT") + 
  theme(plot.title = element_text(hjust = 0.5)) +
  ylab("RT") +
  xlab("Conflict") + 
  guides(fill=guide_legend(title="Conflict")) +
  coord_cartesian(ylim=c(1800,2200))
#ggsave("RT4000.png",width=5,height=5)

# violin plot
ggplot(RT.data.4000, aes(x=Conflict, y=meanRT, color=Conflict)) +
  geom_violin()+ 
  theme_classic()  +
  ggtitle("RT (4000ms cut-off)")  +
  ylab("RT (ms)") +
  xlab("Conflict") + 
  theme(plot.title = element_text(hjust = 0.5)) +
  theme(text = element_text(size=15))+ 
  #geom_dotplot(binaxis='y', stackdir='center', dotsize=1)
  geom_boxplot(width=0.1) +
  scale_color_manual(values=c("#336600", "#990033"))
#ggsave("RT4000ViolinPlot.png",width=5,height=5)


#flips when 4000ms cut-off for trials----
flips.data.4000 = ddply(choiceTrialsClean4000, c("Subj","Conflict"), summarise,
                          meanFlips = mean(flips, na.rm = T),
                          sdDiff = sd(flips, na.rm = T))

flips.data.conflict.4000 = ddply(choiceTrialsClean4000, c("Subj","Conflict"), summarise,
                                 meanFlips = mean(flips, na.rm = T),
                                 sdDiff = sd(flips, na.rm = T))
ddply(flips.data.conflict.4000, c("Conflict"), summarise,
      meanSDDiff = mean(meanFlips, na.rm = T),
      sdSDDiff = sd(meanFlips, na.rm = T))
t.test(meanFlips ~ Conflict, data = flips.data.conflict.4000,paired=TRUE)
cohensD(meanFlips ~ Conflict, data = flips.data.conflict.4000,method="paired")


flips.wide.4000 = dcast(flips.data.4000, Subj ~ Conflict, value.var = "meanFlips")
flips.wide.4000$meanPerSubject = apply(flips.wide.4000[,2:3], 1, mean)
generalMean.flips.4000 = mean(flips.wide.4000$meanPerSubject)
generalMean.flips.4000
sd(flips.wide.4000$meanPerSubject)

flips.subjects.4000=merge(flips.data.4000,flips.wide.4000[,c("Subj","meanPerSubject")])

flips.subjects.4000$standardizedmeanFlips = flips.subjects.4000$meanFlips - flips.subjects.4000$meanPerSubject + generalMean.flips.4000 # Following Cousineau 2005 Tutorials in Quantitative Methods for Psychology 

n.cells = 2
cf = sqrt(n.cells/(n.cells-1)) # Following Morey 2008 in Tutorials in Quantitative Methods for Psychology,
# the correction factor is sqrt(number of overall cells/number of overall cells-1)

flips.groups.4000 = ddply(flips.subjects.4000, c("Conflict"), summarise,
                            mean = mean(meanFlips, na.rm = T),
                            sd = sd(meanFlips, na.rm=T),
                            n=length(unique(Subj)),
                            sdForErrorBars = sd(standardizedmeanFlips, na.rm=T),
                            seForErrorBars.beforeMoreyCorrection=sdForErrorBars/sqrt(n),
                            seForErrorBars = seForErrorBars.beforeMoreyCorrection*cf,
                            CIRT = 1.96*seForErrorBars) #95% Confidence interval

flips.groups.4000

#Graph
ggplot(flips.groups.4000, aes(x=Conflict, y=mean, fill=Conflict)) +
  geom_bar(width=0.8, position=position_dodge(.9), colour="black", stat="identity") +
  geom_errorbar(position=position_dodge(.9), width=.2, aes(ymin=mean-seForErrorBars, ymax=mean+seForErrorBars)) +
  scale_fill_manual(values=c("#336600", "#990033")) + 
  theme_minimal()  +
  ggtitle("flips") + 
  theme(plot.title = element_text(hjust = 0.5)) +
  ylab("flips (0-100)") +
  xlab("Conflict") + 
  guides(fill=guide_legend(title="Conflict")) +
  coord_cartesian(ylim=c(2.2,2.9))
#ggsave("flips4000.png",width=5,height=5)

# violin plot
ggplot(flips.data.4000, aes(x=Conflict, y=meanFlips, color=Conflict)) +
  geom_violin()+ 
  theme_classic()  +
  ggtitle("X-Flips (4000ms cut-off)")  +
  ylab("Mean X-Flips") +
  xlab("Conflict") + 
  theme(plot.title = element_text(hjust = 0.5)) +
  theme(text = element_text(size=15))+ 
  #geom_dotplot(binaxis='y', stackdir='center', dotsize=1)
  geom_boxplot(width=0.1) +
  scale_color_manual(values=c("#336600", "#990033"))
#ggsave("Flips4000ViolinPlot.png",width=5,height=5)

# Regression RT with 4000ms cutoff
contrasts(choiceTrialsClean4000$Conflict)=matrix(c(-1,1), nrow = 2, byrow=T)
contrasts(choiceTrialsClean4000$Conflict)

mixed.model.RT.4000 = lmer(RT ~ Conflict + 
                        (1|Subj),
                      data = choiceTrialsClean4000)
summary(mixed.model.RT.4000)
# LRT for Conflict
mixed.model.RT.compConflict.4000 = lmer(RT ~  +
                                     (1|Subj),
                                   data = choiceTrialsClean4000)
anova(mixed.model.RT.4000, mixed.model.RT.compConflict.4000)

# Regression flips
mixed.model.flips.4000 = lmer(flips ~ Conflict + 
                          (1|Subj),
                        data = choiceTrialsClean4000)
summary(mixed.model.flips.4000)

# LRT for Conflict
mixed.model.flips.compConflict.4000 = lmer(flips ~ +
                                       (1|Subj),
                                     data = choiceTrialsClean4000)
anova(mixed.model.flips.4000, mixed.model.flips.compConflict.4000)


#results when transforming RT with log----
RT.data.log = ddply(choiceTrialsCleaner, c("Subj","Conflict"), summarise,
                    meanRT = mean(logRT, na.rm = T),
                    sdRT = sd(logRT, na.rm = T))
RT.wide.log = dcast(RT.data.log, Subj ~ Conflict, value.var = "meanRT")
RT.wide.log$meanPerSubject = apply(RT.wide.log[,2:3], 1, mean)
generalMean.log = mean(RT.wide.log$meanPerSubject)
generalMean.log
sd(RT.wide.log$meanPerSubject)

RT.subjects.log=merge(RT.data.log,RT.wide.log[,c("Subj","meanPerSubject")])

RT.subjects.log$standardizedMeanRT = RT.subjects.log$meanRT - RT.subjects.log$meanPerSubject + generalMean.log # Following Cousineau 2005 Tutorials in Quantitative Methods for Psychology 

n.cells = 2
cf = sqrt(n.cells/(n.cells-1)) # Following Morey 2008 in Tutorials in Quantitative Methods for Psychology,
# the correction factor is sqrt(number of overall cells/number of overall cells-1)

RT.groups.log = ddply(RT.subjects.log, c("Conflict"), summarise,
                      mean = mean(meanRT, na.rm = T),
                      sd = sd(meanRT, na.rm=T),
                      n=length(unique(Subj)),
                      sdForErrorBars = sd(standardizedMeanRT, na.rm=T),
                      seForErrorBars.beforeMoreyCorrection=sdForErrorBars/sqrt(n),
                      seForErrorBars = seForErrorBars.beforeMoreyCorrection*cf,
                      CIRT = 1.96*seForErrorBars) #95% Confidence interval

RT.groups.log

ddply(RT.subjects.log, c("Conflict"), summarise,
      mean = mean(meanRT, na.rm = T),
      sd = sd(meanRT, na.rm=T))
t.test(meanRT ~ Conflict, data=RT.data.log,paired=T)
cohensD(meanRT ~ Conflict, data=RT.data.log,method="paired")

#Graph
ggplot(RT.groups.log, aes(x=Conflict, y=mean, fill=Conflict)) +
  geom_bar(width=0.8, position=position_dodge(.9), colour="black", stat="identity") +
  geom_errorbar(position=position_dodge(.9), width=.2, aes(ymin=mean-seForErrorBars, ymax=mean+seForErrorBars)) +
  scale_fill_manual(values=c("#336600", "#990033")) + 
  theme_minimal()  +
  ggtitle("RT") + 
  theme(plot.title = element_text(hjust = 0.5)) +
  ylab("RT") +
  xlab("Conflict") + 
  guides(fill=guide_legend(title="Conflict")) +
  coord_cartesian(ylim=c(7.4,7.7))
#ggsave("RT.png",width=5,height=5)


# Regression RT with log transformation
contrasts(choiceTrialsCleaner$Conflict)=matrix(c(-1,1), nrow = 2, byrow=T)
contrasts(choiceTrialsCleaner$Conflict)

mixed.model.RT.log = lmer(logRT ~ Conflict + 
                            (1|Subj),
                          data = choiceTrialsCleaner)
summary(mixed.model.RT.log)

# LRT for Conflict
mixed.model.RT.compConflict.log = lmer(logRT ~ +
                                         (1|Subj),
                                       data = choiceTrialsCleaner)
anova(mixed.model.RT.log, mixed.model.RT.compConflict.log)

# switching cost----
#removing trials with NA in conflict or previous conflict
choiceTrialsGratton = subset(choiceTrialsCleaner, is.na(Previous_Conflict)==F)

summary(choiceTrialsGratton)
choiceTrialsGratton$Previous_Conflict = as.factor(choiceTrialsGratton$Previous_Conflict)
choiceTrialsGratton$taskSwitch = as.factor(choiceTrialsGratton$taskSwitch)

RT.data.Gratton.anova = ddply(choiceTrialsGratton, c("Subj","Conflict","taskSwitch"), summarise,
                              meanRT = mean(RT, na.rm = T),
                              sdRT = sd(RT, na.rm = T))

ezANOVA.RT.G = ezANOVA(data=RT.data.Gratton.anova, dv=meanRT, wid=Subj, within=c(Conflict,taskSwitch),type=3,detailed=FALSE)

apa.ezANOVA.table(ezANOVA.RT.G)
#apa.ezANOVA.table(ezANOVA.RT.G,table.number=99,filename="APA_ANOVA_myGratton.doc")

#aggeragating data for gratton
generalMean.g = mean(RT.data.Gratton.anova$meanRT)
generalMean.g

RT.wide.g = dcast(RT.data.Gratton.anova, Subj ~ Conflict + taskSwitch, value.var = "meanRT")
RT.wide.g$meanPerSubject = apply(RT.wide.g[,2:5], 1, mean)

RT.subjects.g=merge(RT.data.Gratton.anova,RT.wide.g[,c("Subj","meanPerSubject")])

RT.subjects.g$standardizedMeanRT = RT.subjects.g$meanRT - RT.subjects.g$meanPerSubject + generalMean.g # Following Cousineau 2005 Tutorials in Quantitative Methods for Psychology

n.cells = 4
cf = sqrt(n.cells/(n.cells-1)) # Following Morey 2008 in Tutorials in Quantitative Methods for Psychology,
# the correction factor is sqrt(number of overall cells/number of overall cells-1)

RT.groups.c.g = ddply(RT.subjects.g, c("Conflict","taskSwitch"), summarise,
                      mean = mean(meanRT, na.rm = T),
                      sd = sd(meanRT, na.rm=T),
                      n=length(unique(Subj)),
                      sdForErrorBars = sd(standardizedMeanRT, na.rm=T),
                      seForErrorBars.beforeMoreyCorrection=sdForErrorBars/sqrt(n),
                      seForErrorBars = seForErrorBars.beforeMoreyCorrection*cf,
                      CIRT = 1.96*seForErrorBars) #95% Confidence interval

RT.groups.c.g

ggplot(RT.groups.c.g, aes(x=Conflict, y=mean, fill=taskSwitch)) +
  geom_bar(width=0.8, position=position_dodge(.9), colour="black", stat="identity") +
  geom_errorbar(position=position_dodge(.9), width=.2, aes(ymin=mean-seForErrorBars, ymax=mean+seForErrorBars)) +
  scale_fill_manual(values=c("yellow", "blue")) +
  theme_minimal()  +
  ggtitle("RT") +
  theme(plot.title = element_text(hjust = 0.5)) +
  ylab("RT") +
  guides(fill=guide_legend(title="Trial type")) +
  coord_cartesian(ylim=c(1800,2400))
#ggsave("RTforGrattonbytrialTypeXAxis.png",width=5,height=5)

ggplot(RT.groups.c.g, aes(x=taskSwitch, y=mean, fill=Conflict)) +
  geom_bar(width=0.8, position=position_dodge(.9), colour="black", stat="identity") +
  geom_errorbar(position=position_dodge(.9), width=.2, aes(ymin=mean-seForErrorBars, ymax=mean+seForErrorBars)) +
  scale_fill_manual(values=c("#336600", "#990033")) +
  theme_minimal()  +
  ggtitle("RT") +
  theme(plot.title = element_text(hjust = 0.5)) +
  ylab("RT") +
  xlab("Trial type") +
  guides(fill=guide_legend(title="Conflict")) +
  coord_cartesian(ylim=c(1800,2400))
#ggsave("RTforGrattonbytrialType.png",width=5,height=5)

# switching cost on flips----
#removing trials with NA in conflict or previous conflict
choiceTrialsGrattonFlips = subset(choiceTrialsClean, is.na(Previous_Conflict)==F)

summary(choiceTrialsGrattonFlips)
choiceTrialsGrattonFlips$Previous_Conflict = as.factor(choiceTrialsGrattonFlips$Previous_Conflict)
choiceTrialsGrattonFlips$taskSwitch = as.factor(choiceTrialsGrattonFlips$taskSwitch)

Flips.data.Gratton.anova = ddply(choiceTrialsGrattonFlips, c("Subj","Conflict","taskSwitch"), summarise,
                                 meanflips = mean(flips, na.rm = T),
                                 sdflips = sd(flips, na.rm = T))

ezANOVA.flips.G = ezANOVA(data=Flips.data.Gratton.anova, dv=meanflips, wid=Subj, within=c(Conflict,taskSwitch),type=3,detailed=FALSE)

apa.ezANOVA.table(ezANOVA.flips.G)
#apa.ezANOVA.table(ezANOVA.flips.G,table.number=99,filename="APA_ANOVA_myGratton_on_flips.doc")

#aggeragating data for switching cost
generalMean.g.flips = mean(Flips.data.Gratton.anova$meanflips)
generalMean.g.flips

flips.wide.g = dcast(Flips.data.Gratton.anova, Subj ~ Conflict + taskSwitch, value.var = "meanflips")
flips.wide.g$meanPerSubject = apply(flips.wide.g[,2:5], 1, mean)

flips.subjects.g=merge(Flips.data.Gratton.anova,flips.wide.g[,c("Subj","meanPerSubject")])

flips.subjects.g$standardizedMeanflips = flips.subjects.g$meanflips - flips.subjects.g$meanPerSubject + generalMean.g.flips # Following Cousineau 2005 Tutorials in Quantitative Methods for Psychology

n.cells = 4
cf = sqrt(n.cells/(n.cells-1)) # Following Morey 2008 in Tutorials in Quantitative Methods for Psychology,
# the correction factor is sqrt(number of overall cells/number of overall cells-1)

flips.groups.c.g = ddply(flips.subjects.g, c("Conflict","taskSwitch"), summarise,
                         mean = mean(meanflips, na.rm = T),
                         sd = sd(meanflips, na.rm=T),
                         n=length(unique(Subj)),
                         sdForErrorBars = sd(standardizedMeanflips, na.rm=T),
                         seForErrorBars.beforeMoreyCorrection=sdForErrorBars/sqrt(n),
                         seForErrorBars = seForErrorBars.beforeMoreyCorrection*cf,
                         CIRT = 1.96*seForErrorBars) #95% Confidence interval

flips.groups.c.g

ggplot(flips.groups.c.g, aes(x=Conflict, y=mean, fill=taskSwitch)) +
  geom_bar(width=0.8, position=position_dodge(.9), colour="black", stat="identity") +
  geom_errorbar(position=position_dodge(.9), width=.2, aes(ymin=mean-seForErrorBars, ymax=mean+seForErrorBars)) +
  scale_fill_manual(values=c("yellow", "blue")) +
  theme_minimal()  +
  ggtitle("flips") +
  theme(plot.title = element_text(hjust = 0.5)) +
  ylab("flips") +
  guides(fill=guide_legend(title="Trial type")) +
  coord_cartesian(ylim=c(2.2,3.5))
#ggsave("flipsforGrattonbytrialTypeXAxis.png",width=5,height=5)

ggplot(flips.groups.c.g, aes(x=taskSwitch, y=mean, fill=Conflict)) +
  geom_bar(width=0.8, position=position_dodge(.9), colour="black", stat="identity") +
  geom_errorbar(position=position_dodge(.9), width=.2, aes(ymin=mean-seForErrorBars, ymax=mean+seForErrorBars)) +
  scale_fill_manual(values=c("#336600", "#990033")) +
  theme_minimal()  +
  ggtitle("flips") +
  theme(plot.title = element_text(hjust = 0.5)) +
  ylab("flips") +
  xlab("Trial type") +
  guides(fill=guide_legend(title="Conflict")) +
  coord_cartesian(ylim=c(2.2,3.5))
#ggsave("flipsforGrattonbytrialType.png",width=5,height=5)

# flips.subjects.g.ap=subset(flips.subjects.g,Conflict=="AP-AP")
# flips.subjects.g.av=subset(flips.subjects.g,Conflict=="AV-AV")
# t.test(meanflips ~ taskSwitch, data=flips.subjects.g.ap,paired=T)
# cohensD(meanflips ~ taskSwitch, data=flips.subjects.g.ap,method="paired")
# 
# t.test(meanflips ~ taskSwitch, data=flips.subjects.g.av,paired=T)
# cohensD(meanflips ~ taskSwitch, data=flips.subjects.g.av,method="paired")

# switching cost on MD----
#removing trials with NA in conflict or previous conflict
choiceTrialsGrattonMD = subset(choiceTrialsClean, is.na(Previous_Conflict)==F)

summary(choiceTrialsGrattonMD)
choiceTrialsGrattonMD$Previous_Conflict = as.factor(choiceTrialsGrattonMD$Previous_Conflict)
choiceTrialsGrattonMD$taskSwitch = as.factor(choiceTrialsGrattonMD$taskSwitch)

MD.data.Gratton.anova = ddply(choiceTrialsGrattonMD, c("Subj","Conflict","taskSwitch"), summarise,
                              meanMD = mean(max_deviation, na.rm = T),
                              sdMD = sd(max_deviation, na.rm = T))

ezANOVA.MD.G = ezANOVA(data=MD.data.Gratton.anova, dv=meanMD, wid=Subj, within=c(Conflict,taskSwitch),type=3,detailed=FALSE)

apa.ezANOVA.table(ezANOVA.MD.G)
#apa.ezANOVA.table(ezANOVA.MD.G,table.number=99,filename="APA_ANOVA_myGratton_on_MD.doc")

#aggeragating data for switching cost
generalMean.g.MD = mean(MD.data.Gratton.anova$meanMD)
generalMean.g.MD

MD.wide.g = dcast(MD.data.Gratton.anova, Subj ~ Conflict + taskSwitch, value.var = "meanMD")
MD.wide.g$meanPerSubject = apply(MD.wide.g[,2:5], 1, mean)

MD.subjects.g=merge(MD.data.Gratton.anova,MD.wide.g[,c("Subj","meanPerSubject")])

MD.subjects.g$standardizedMeanMD = MD.subjects.g$meanMD - MD.subjects.g$meanPerSubject + generalMean.g.MD # Following Cousineau 2005 Tutorials in Quantitative Methods for Psychology

n.cells = 4
cf = sqrt(n.cells/(n.cells-1)) # Following Morey 2008 in Tutorials in Quantitative Methods for Psychology,
# the correction factor is sqrt(number of overall cells/number of overall cells-1)

MD.groups.c.g = ddply(MD.subjects.g, c("Conflict","taskSwitch"), summarise,
                      mean = mean(meanMD, na.rm = T),
                      sd = sd(meanMD, na.rm=T),
                      n=length(unique(Subj)),
                      sdForErrorBars = sd(standardizedMeanMD, na.rm=T),
                      seForErrorBars.beforeMoreyCorrection=sdForErrorBars/sqrt(n),
                      seForErrorBars = seForErrorBars.beforeMoreyCorrection*cf,
                      CIRT = 1.96*seForErrorBars) #95% Confidence interval

MD.groups.c.g

ggplot(MD.groups.c.g, aes(x=Conflict, y=mean, fill=taskSwitch)) +
  geom_bar(width=0.8, position=position_dodge(.9), colour="black", stat="identity") +
  geom_errorbar(position=position_dodge(.9), width=.2, aes(ymin=mean-seForErrorBars, ymax=mean+seForErrorBars)) +
  scale_fill_manual(values=c("yellow", "blue")) +
  theme_minimal()  +
  ggtitle("MD") +
  theme(plot.title = element_text(hjust = 0.5)) +
  ylab("MD") +
  guides(fill=guide_legend(title="Trial type")) +
  coord_cartesian(ylim=c(0.6,1.0))
#ggsave("MDforGrattonbytrialTypeXAxis.png",width=5,height=5)

ggplot(MD.groups.c.g, aes(x=taskSwitch, y=mean, fill=Conflict)) +
  geom_bar(width=0.8, position=position_dodge(.9), colour="black", stat="identity") +
  geom_errorbar(position=position_dodge(.9), width=.2, aes(ymin=mean-seForErrorBars, ymax=mean+seForErrorBars)) +
  scale_fill_manual(values=c("#336600", "#990033")) +
  theme_minimal()  +
  ggtitle("MD") +
  theme(plot.title = element_text(hjust = 0.5)) +
  ylab("MD (0-100)") +
  xlab("Trial type") +
  guides(fill=guide_legend(title="Conflict")) +
  coord_cartesian(ylim=c(0.6,1.0))
#ggsave("MDforGrattonbytrialType.png",width=5,height=5)

# MD.subjects.g.ap=subset(MD.subjects.g,Conflict=="AP-AP")
# MD.subjects.g.av=subset(MD.subjects.g,Conflict=="AV-AV")
# t.test(meanMD ~ taskSwitch, data=MD.subjects.g.ap,paired=T)
# cohensD(meanMD ~ taskSwitch, data=MD.subjects.g.ap,method="paired")
# 
# t.test(meanMD ~ taskSwitch, data=MD.subjects.g.av,paired=T)
# cohensD(meanMD ~ taskSwitch, data=MD.subjects.g.av,method="paired")

# switching cost on InitialRT----
#removing trials with NA in conflict or previous conflict
choiceTrialsGrattonInitialRT = subset(choiceTrialsClean, is.na(Previous_Conflict)==F)

summary(choiceTrialsGrattonInitialRT)
choiceTrialsGrattonInitialRT$Previous_Conflict = as.factor(choiceTrialsGrattonInitialRT$Previous_Conflict)
choiceTrialsGrattonInitialRT$taskSwitch = as.factor(choiceTrialsGrattonInitialRT$taskSwitch)

InitialRT.data.Gratton.anova = ddply(choiceTrialsGrattonInitialRT, c("Subj","Conflict","taskSwitch"), summarise,
                                     meanInitialRT = mean(first_movement_time, na.rm = T),
                                     sdInitialRT = sd(first_movement_time, na.rm = T))

ezANOVA.InitialRT.G = ezANOVA(data=InitialRT.data.Gratton.anova, dv=meanInitialRT, wid=Subj, within=c(Conflict,taskSwitch),type=3,detailed=FALSE)

apa.ezANOVA.table(ezANOVA.InitialRT.G)
#apa.ezANOVA.table(ezANOVA.InitialRT.G,table.number=99,filename="APA_ANOVA_myGratton_on_InitialRT.doc")

#aggeragating data for switching cost
generalMean.g.InitialRT = mean(InitialRT.data.Gratton.anova$meanInitialRT)
generalMean.g.InitialRT

InitialRT.wide.g = dcast(InitialRT.data.Gratton.anova, Subj ~ Conflict + taskSwitch, value.var = "meanInitialRT")
InitialRT.wide.g$meanPerSubject = apply(InitialRT.wide.g[,2:5], 1, mean)

InitialRT.subjects.g=merge(InitialRT.data.Gratton.anova,InitialRT.wide.g[,c("Subj","meanPerSubject")])

InitialRT.subjects.g$standardizedMeanInitialRT = InitialRT.subjects.g$meanInitialRT - InitialRT.subjects.g$meanPerSubject + generalMean.g.InitialRT # Following Cousineau 2005 Tutorials in Quantitative Methods for Psychology

n.cells = 4
cf = sqrt(n.cells/(n.cells-1)) # Following Morey 2008 in Tutorials in Quantitative Methods for Psychology,
# the correction factor is sqrt(number of overall cells/number of overall cells-1)

InitialRT.groups.c.g = ddply(InitialRT.subjects.g, c("Conflict","taskSwitch"), summarise,
                             mean = mean(meanInitialRT, na.rm = T),
                             sd = sd(meanInitialRT, na.rm=T),
                             n=length(unique(Subj)),
                             sdForErrorBars = sd(standardizedMeanInitialRT, na.rm=T),
                             seForErrorBars.beforeMoreyCorrection=sdForErrorBars/sqrt(n),
                             seForErrorBars = seForErrorBars.beforeMoreyCorrection*cf,
                             CIRT = 1.96*seForErrorBars) #95% Confidence interval

InitialRT.groups.c.g

ggplot(InitialRT.groups.c.g, aes(x=Conflict, y=mean, fill=taskSwitch)) +
  geom_bar(width=0.8, position=position_dodge(.9), colour="black", stat="identity") +
  geom_errorbar(position=position_dodge(.9), width=.2, aes(ymin=mean-seForErrorBars, ymax=mean+seForErrorBars)) +
  scale_fill_manual(values=c("yellow", "blue")) +
  theme_minimal()  +
  ggtitle("InitialRT") +
  theme(plot.title = element_text(hjust = 0.5)) +
  ylab("InitialRT") +
  guides(fill=guide_legend(title="Trial type")) +
  coord_cartesian(ylim=c(300,350))
#ggsave("InitialRTforGrattonbytrialTypeXAxis.png",width=5,height=5)

ggplot(InitialRT.groups.c.g, aes(x=taskSwitch, y=mean, fill=Conflict)) +
  geom_bar(width=0.8, position=position_dodge(.9), colour="black", stat="identity") +
  geom_errorbar(position=position_dodge(.9), width=.2, aes(ymin=mean-seForErrorBars, ymax=mean+seForErrorBars)) +
  scale_fill_manual(values=c("#336600", "#990033")) +
  theme_minimal()  +
  ggtitle("InitialRT") +
  theme(plot.title = element_text(hjust = 0.5)) +
  ylab("InitialRT") +
  xlab("Trial type") +
  guides(fill=guide_legend(title="Conflict")) +
  coord_cartesian(ylim=c(300,350))
#ggsave("InitialRTforGrattonbytrialType.png",width=5,height=5)

# InitialRT.subjects.g.ap=subset(InitialRT.subjects.g,Conflict=="AP-AP")
# InitialRT.subjects.g.av=subset(InitialRT.subjects.g,Conflict=="AV-AV")
# t.test(meanInitialRT ~ taskSwitch, data=InitialRT.subjects.g.ap,paired=T)
# cohensD(meanInitialRT ~ taskSwitch, data=InitialRT.subjects.g.ap,method="paired")
# 
# t.test(meanInitialRT ~ taskSwitch, data=InitialRT.subjects.g.av,paired=T)
# cohensD(meanInitialRT ~ taskSwitch, data=InitialRT.subjects.g.av,method="paired")
