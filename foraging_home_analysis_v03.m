

clearvars
close all


histtimemax = 30;
plottimemax = 2500;
startdate = [2018,03,29; 2018,03,29; 2018,01,01; 2018,01,01;
    2018,01,01; 2018,01,01; 2018,03,29];


dataFolder = '~/Documents/python/rPi/data/';

fileList1 = dir([dataFolder,'*.log']);
fileList2 = dir([dataFolder,'*.dat']);

monkNames = {'O','K','H','L','A','S','Q'};

monkList = zeros(length(fileList1),1);
taskList = zeros(length(fileList1),1);
dateList = zeros(length(fileList1),1);
dayList = zeros(length(fileList1),1);
monthList = zeros(length(fileList1),1);

for ff=1:length(fileList1)
    parsed = sscanf(fileList1(ff).name,'monkey%i_task%i_%i-%i-%i_%i-%i-%i.log');
    
    monkList(ff) = parsed(1);
    taskList(ff) = parsed(2);
    dateList(ff) = datenum(parsed(3),parsed(4),parsed(5),parsed(6),parsed(7),parsed(8));
    dayList(ff) = parsed(5);
    monthList(ff) = parsed(4);
    
    trainday(ff) = datenum([parsed(3),parsed(4),parsed(5)])-datenum(startdate(monkList(ff),:))+1;
end



%% plot data for task 1
task1list = find(taskList==1);

timeMax = 2000;

colTable = lines(length(task1list));
for ff=1:length(task1list)
    
    fprintf('\nFile %i/%i: %s',ff,length(task1list), fileList2(task1list(ff)).name);
    
%     dat1 = dlmread([dataFolder,fileList1(task1list(ff)).name],',',1,0);
    dat2 = dlmread([dataFolder,fileList2(task1list(ff)).name],',',1,0);
    
    timeClick{ff} = dat2((dat2(2:end,7)-dat2(1:end-1,7))>0,1);
    correctClick{ff} = dat2((dat2(2:end,7)-dat2(1:end-1,7))>0,6);
%     timeTot = [timeTot;timeClick{ff}(:)];
%     correctTot = [correctTot;correctClick{ff}(:)];
    
    
%     timeClick{ff} = dat1(dat1(:,2)==1,1);
%     timeMax(ff) = max(timeClick{ff});
    
%     legFields{ff} = [monkNames{monkList(task1list(ff))} ', ' [num2str(monthList(task1list(ff))) '/' num2str(dayList(task1list(ff)))]];
    legFields{ff} = [monkNames{monkList(task1list(ff))} ', ' [num2str(monthList(task1list(ff))) '/' num2str(dayList(task1list(ff)))], ', ', num2str(length(correctClick{ff}))];
    
    figure(1)
    hold on
    plot(timeClick{ff}',ff*ones(size(timeClick{ff}))','o','Color',colTable(ff,:))
    
    figure(2)
    hold on
    plot(timeClick{ff}',(1:length(timeClick{ff}))./length(timeClick{ff}),'Color',colTable(ff,:))
    
    figure(3)
    hold on
    [vHist(ff,:),bHist(ff,:)] = hist(timeClick{ff}(2:end)-timeClick{ff}(1:end-1),linspace(0,histtimemax,41));
    vHist(ff,:) = vHist(ff,:)./(length(timeClick{ff})-1);
    plot(bHist(ff,:),vHist(ff,:),'Color',colTable(ff,:))
    
end

figure(1)
axis([0,plottimemax,0,length(task1list)+1])
% legend(legFields)
set(gca,'YTick',1:length(legFields),'YTickLabel',legFields)
xlabel('Time (sec)')
ylabel('Session')

figure(2)
axis([0,max(timeMax),0,1])
legend(legFields)

figure(3)
legend(legFields)
hold on
plot(mean(bHist),nanmean(vHist),'k','LineWidth',4)
xlabel('Inter-clicks interval (sec)')
ylabel('Density')

figure(4)
bar(bHist',vHist','EdgeColor','none')



% 
% %% plot data for task 2
% clear dat1 dat2 legFields timeClick timeMax
% 
% task2list = find(taskList==2);
% 
% timeTot = [];
% correctTot = [];
% 
% colTable = lines(7);
% for ff=1:length(task2list)
%     
%     fprintf('\nFile %i/%i: %s',ff,length(task2list), fileList2(task2list(ff)).name);
%     
%     dat2 = dlmread([dataFolder,fileList2(task2list(ff)).name],',',1,0);
%     
%     
%     timeClick{ff} = dat2((dat2(2:end,7)-dat2(1:end-1,7))>0,1);
%     correctClick{ff} = dat2((dat2(2:end,7)-dat2(1:end-1,7))>0,6);
%     timeTot = [timeTot;timeClick{ff}(:)];
%     correctTot = [correctTot;correctClick{ff}(:)];
%     
%     nClicksList(task2list(ff)) = length(timeClick{ff});
%     
%     rateUp(ff) = mean(dat2(:,6));
%     
%     probClickUp(ff) = sum(dat2((dat2(2:end,7)-dat2(1:end-1,7))>0,6)==1)./sum(dat2(:,6));
%     probClickDown(ff) = sum(dat2((dat2(2:end,7)-dat2(1:end-1,7))>0,6)==0)./sum(dat2(:,6)==0);
%     
%     nbins = 10;
%     binsize = ceil(length(correctClick{ff})/nbins);
%     binlist = round(linspace(1,(length(correctClick{ff})-binsize),nbins));
%     for bb=1:nbins
%         rateCorrect(bb,ff) = mean(correctClick{ff}(binlist(bb)+(1:binsize)));
%         rateCorrectWeight(bb,ff) = binsize;
%     end
%     
%     
%     timeMax(ff) = max(timeClick{ff});
%     
%     legFields{ff} = [monkNames{monkList(task2list(ff))} ', ' [num2str(monthList(task2list(ff))) '/' num2str(dayList(task2list(ff)))]];
%     
%     figure(11)
%     hold on
%     plot(timeClick{ff}',ff*ones(size(timeClick{ff}))','ko')
%     plot(timeClick{ff}(correctClick{ff}==1)',ff*ones(size(timeClick{ff}(correctClick{ff}==1)))'-0.2,'go',timeClick{ff}(correctClick{ff}==0)',ff*ones(size(timeClick{ff}(correctClick{ff}==0)))'+0.2,'ro')
% %     plot(timeClick{ff}(correctClick{ff}==1)',ff*ones(size(timeClick{ff}(correctClick{ff}==1)))','go',timeClick{ff}(correctClick{ff}==0)',ff*ones(size(timeClick{ff}(correctClick{ff}==0)))','ro')
%     
%     figure(12)
%     hold on
%     plot(timeClick{ff}',(1:length(timeClick{ff}))./length(timeClick{ff}),'Color',colTable(ff,:))
%     
%     figure(13)
%     hold on
%     [vHist(ff,:),bHist(ff,:)] = hist(timeClick{ff}(2:end)-timeClick{ff}(1:end-1),linspace(0,histtimemax,41));
%     vHist(ff,:) = vHist(ff,:)./length(timeClick{ff}-1);
%     plot(bHist(ff,:),vHist(ff,:),'Color',colTable(ff,:))
%     
%     figure(15)
%     hold on
%     pp = polyfit((0.5:length(rateCorrect(:,ff))-0.5)./nbins,rateCorrect(:,ff)',1);
%     plot((0.5:length(rateCorrect(:,ff))-0.5)./nbins,rateCorrect(:,ff),'Color',colTable(ff,:))
% %     plot((0.5:length(rateCorrect(:,ff))-0.5)./nbins,polyval(pp,(0.5:length(rateCorrect(:,ff))-0.5)./nbins),'Color',colTable(ff,:),'LineWidth',2);
%     
%     figure(16)
%     hold on
%     plot(trainday(task2list(ff)), mean(correctClick{ff}), 'o', 'Color',colTable(monkList(task2list(ff)),:),'MarkerSize',sqrt(nClicksList(task2list(ff))))
%     
%     figure(17)
%     hold on
%     plot(trainday(task2list(ff)), mean(correctClick{ff})./rateUp(ff), 'o', 'Color',colTable(monkList(task2list(ff)),:),'MarkerSize',sqrt(nClicksList(task2list(ff))))
%     
%     
%     corrDayList(task2list(ff)) =  mean(correctClick{ff});
%     
% end
% 
% figure(11)
% axis([0,plottimemax,0,length(task2list)+1])
% set(gca,'YTick',1:length(legFields),'YTickLabel',legFields)
% xlabel('Time (sec)')
% ylabel('Session')
% 
% figure(12)
% axis([0,max(timeMax),0,1])
% legend(legFields)
% 
% figure(13)
% legend(legFields)
% hold on
% plot(mean(bHist),mean(vHist),'k','LineWidth',4)
% xlabel('Inter-clicks interval (sec)')
% ylabel('Density')
% 
% figure(14)
% legend(legFields)
% bar(bHist',vHist','EdgeColor','none')
%     
% figure(15)
% legend(legFields)
% % errorbar((0.5:length(rateCorrect(:,ff))-0.5)./nbins,mean(rateCorrect,2),std(rateCorrect,[],2)./sqrt(length(task2list)),'k','LineWidth',4)
% errorbar((0.5:length(rateCorrect(:,ff))-0.5)./nbins,sum(rateCorrect.*rateCorrectWeight,2)./sum(rateCorrectWeight,2),std(rateCorrect,[],2)./sqrt(length(task2list)),'k','LineWidth',4)
% axis([0,1,0,1])
% 
% 
% dayMax = 12;
% 
% figure(16)
% axis([0,dayMax,0,1])
% set(gca,'XTick',1:dayMax)
% xlabel('Training day')
% ylabel('Correlation')
% 
% 
% % do some stats
% for mm=[1,2,7]
%     dd = trainday((taskList==2)&(monkList==mm))';
%     cc = corrDayList((taskList==2)&(monkList==mm))';
%     ww = nClicksList((taskList==2)&(monkList==mm))';
%     pp = (diag(ww)*[ones(size(dd)),dd])\(ww.*cc);
%     figure(16)
%     hold on
%     plot(dd,[ones(size(dd)),dd]*pp,'Color',colTable(mm,:))
% end
% 


