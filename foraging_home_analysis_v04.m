

clearvars
close all


histtimemax = 30;
plottimemax = 5000;
startdate = [2018,03,29; 2018,03,29; 2018,03,29; 2018,03,29;
    2018,03,29; 2018,03,29; 2018,03,29];


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




%% plot data for task 2
clear dat1 dat2 legFields timeClick timeMax

task2list = find(taskList==2);

temp = sortrows([monkList(task2list),dayList(task2list),(1:length(task2list))'],[1,2,3]);
temp = sortrows([temp(:,3),(1:length(task2list))'],1);
plotOrder = temp(:,2);

timeTot = [];
correctTot = [];

colTable = lines(7);
for ff=1:length(task2list)
    
    fprintf('\nFile %i/%i: %s',ff,length(task2list), fileList2(task2list(ff)).name);
    
    dat2 = dlmread([dataFolder,fileList2(task2list(ff)).name],',',1,0);
    
    monkList2(ff) = monkList(task2list(ff));
    trainDay2(ff) = trainday(task2list(ff));
    
    clickTimes{ff} = dat2((dat2(2:end,7)-dat2(1:end-1,7))>0,1);
    clickCorrect{ff} = dat2([(dat2(2:end,7)-dat2(1:end-1,7))>0;0]&(dat2(:,6)==1),1);
    clickWrong{ff} = dat2([(dat2(2:end,7)-dat2(1:end-1,7))>0;0]&(dat2(:,6)==0),1);
    clickVal{ff} = dat2((dat2(2:end,7)-dat2(1:end-1,7))>0,6);
    
    nbins = 10;
    binsize = ceil(length(clickTimes{ff})/nbins);
    binlist = round(linspace(1,(length(clickTimes{ff})-binsize),nbins));
    for bb=1:nbins
        rateCorrect(bb,ff) = mean(clickVal{ff}(binlist(bb)+(1:binsize)));
        rateCorrectWeight(bb,ff) = binsize;
    end
    
    minClickInt = 1;
    rmInd = false(size(clickTimes{ff}));
    for cc=2:length(clickTimes{ff})
        if (clickTimes{ff}(cc)-clickTimes{ff}(cc-1))<minClickInt
            rmInd(cc) = true;
        end
    end
    clickTimes{ff}(rmInd) = [];
    rmInd = false(size(clickCorrect{ff}));
    for cc=1:length(clickCorrect{ff})
        if sum(clickTimes{ff}==clickCorrect{ff}(cc))==0
            rmInd(cc) = true;
        end
    end
    clickCorrect{ff}(rmInd) = [];
    rmInd = false(size(clickWrong{ff}));
    for cc=1:length(clickWrong{ff})
        if sum(clickTimes{ff}==clickWrong{ff}(cc))==0
            rmInd(cc) = true;
        end
    end
    clickWrong{ff}(rmInd) = [];
    
    rewardsNum(ff) = length(clickCorrect{ff});
    rewardsRate(ff) = length(clickCorrect{ff})./length(clickTimes{ff});
    
    switchTimes{ff} = dat2((dat2(2:end,6)-dat2(1:end-1,6))~=0,1);
    switchUp{ff} = [0;dat2((dat2(2:end,6)-dat2(1:end-1,6))>0,1)];
    switchDown{ff} = dat2((dat2(2:end,6)-dat2(1:end-1,6))<0,1);
    
    nbins = 10;
    binlist = linspace(0,dat2(end,1),nbins+1);
    for bb=1:nbins
        rateTimeout(bb,ff) = mean(dat2((dat2(:,1)>binlist(bb))&(dat2(:,1)<binlist(bb+1)),8));
    end
    
    for cc=1:length(clickCorrect{ff})
        clickDelayCorrect{ff}(cc) = clickCorrect{ff}(cc)-switchUp{ff}(find(switchUp{ff}<clickCorrect{ff}(cc),1,'last'));
    end
    ccfirst = 0;
    for cc=1:length(clickWrong{ff})
        lastSwitch = switchDown{ff}(find(switchDown{ff}<clickWrong{ff}(cc),1,'last'));
        clickDelayWrong{ff}(cc) = clickWrong{ff}(cc)-lastSwitch;
        if (clickWrong{ff}(cc)==clickWrong{ff}(find(clickWrong{ff}>lastSwitch,1,'first')))
            ccfirst = ccfirst+1;
            clickDelayWrongFirst{ff}(ccfirst) = clickWrong{ff}(cc)-lastSwitch;
        end
    end
    
    [vHist(ff,:),bHist(ff,:)] = hist(clickTimes{ff}(2:end)-clickTimes{ff}(1:end-1),linspace(0,histtimemax,41));
    vHist(ff,:) = vHist(ff,:)./length(clickTimes{ff}-1);
    
    [vHistCorrect(ff,:),bHistCorrect(ff,:)] = hist(clickDelayCorrect{ff},linspace(0,histtimemax,41));
    [vHistWrong(ff,:),bHistWrong(ff,:)] = hist(clickDelayWrong{ff},linspace(0,histtimemax,41));
    [vHistWrongFirst(ff,:),bHistWrongFirst(ff,:)] = hist(clickDelayWrongFirst{ff},linspace(0,histtimemax,41));
    vHistCorrect(ff,:) = vHistCorrect(ff,:)./length(clickDelayCorrect{ff});
    vHistWrong(ff,:) = vHistWrong(ff,:)./length(clickDelayWrong{ff});
    vHistWrongFirst(ff,:) = vHistWrongFirst(ff,:)./length(clickDelayWrongFirst{ff});
    
    cumProbCorrect(:,ff) = cumsum(vHistCorrect(ff,:));
    cumProbWrong(:,ff) = cumsum(vHistWrong(ff,:));
    cumProbWrongFirst(:,ff) = cumsum(vHistWrong(ff,:));
    aucClickDelay(ff) = trapz(cumsum(vHistWrong(ff,:)),cumsum(vHistCorrect(ff,:)));
    aucClickDelayFirst(ff) = trapz(cumsum(vHistWrongFirst(ff,:)),cumsum(vHistCorrect(ff,:)));
    
    timeMax(ff) = max(clickTimes{ff});
    legFields{plotOrder(ff)} = [monkNames{monkList(task2list(ff))} ', ' [num2str(monthList(task2list(ff))) '/' num2str(dayList(task2list(ff)))], ', ', num2str(length(clickCorrect{ff}))];
    
    
    figure(11)
    hold on
    plot(clickCorrect{ff},plotOrder(ff)*ones(size(clickCorrect{ff}))-0.1,'g.',clickWrong{ff},plotOrder(ff)*ones(size(clickWrong{ff}))+0.1,'r.')
    if size(dat2,2)==8
        if size(dat2(dat2(2:end,8)-dat2(1:end-1,8)>0,1),1)==size(dat2(dat2(2:end,8)-dat2(1:end-1,8)<0,1),1)
            timeout = [dat2(dat2(2:end,8)-dat2(1:end-1,8)>0,1),dat2(dat2(2:end,8)-dat2(1:end-1,8)<0,1)];
        else
            timeout = [dat2(dat2(2:end,8)-dat2(1:end-1,8)>0,1),[dat2(dat2(2:end,8)-dat2(1:end-1,8)<0,1);dat2(end,1)]];
        end
        clickTimeout(ff) = mean(dat2([(dat2(2:end,7)-dat2(1:end-1,7))>0;0]&(dat2(:,6)==0),8));
        
        plot(timeout',plotOrder(ff)*ones(size(timeout))','k')
    else
        clickTimeout(ff) = 0;
    end
    
    figure(12)
    subplot(1,2,1)
    hold on
    plot(clickTimes{ff},(1:length(clickTimes{ff}))./length(clickTimes{ff}),'Color',colTable(monkList2(ff),:))
    subplot(1,2,2)
    hold on
    plot(clickTimes{ff},(1:length(clickTimes{ff}))./length(clickTimes{ff}),'Color',colTable(monkList2(ff),:))
    
    % plot ratio correct
    figure(13)
    hold on
    plot(trainday(task2list(ff)),rewardsRate(ff),'o','MarkerSize',sqrt(length(clickTimes{ff})),'Color',colTable(monkList2(ff),:))
    
    % plot ratio timeout
    figure(14)
    hold on
    plot(trainday(task2list(ff)),clickTimeout(ff),'o','MarkerSize',sqrt(length(clickTimes{ff})),'Color',colTable(monkList2(ff),:))
    
    %plot ratio correct within session
    figure(15)
    hold on
    plot(1:nbins,rateCorrect(:,ff),'Color',colTable(monkList2(ff),:))
    
    %plot ratio time out within session
    figure(16)
    hold on
    plot(1:nbins,rateTimeout(:,ff),'Color',colTable(monkList2(ff),:))
    
    
    % plot RT distr
    figure(21)
    hold on
    plot(bHist(ff,:),vHist(ff,:),'Color',colTable(monkList2(ff),:))
    
    % plot distr, ROC and AUC
    figure(22)
    subplot(1,3,1)
    hold on
    plot(bHistCorrect(ff,:),vHistCorrect(ff,:),'--g',bHistWrong(ff,:),vHistWrong(ff,:),'--r')
    subplot(1,3,2)
    hold on
    plot(cumProbWrong(:,ff),cumProbCorrect(:,ff),'--k')
    subplot(1,3,3)
    hold on
    plot(trainday(task2list(ff)),aucClickDelay(ff),'o','MarkerSize',sqrt(length(clickTimes{ff})),'Color',colTable(monkList2(ff),:))
    
    % plot distr, ROC and AUC for first click after switch only
    figure(23)
    subplot(1,3,1)
    hold on
    plot(bHistCorrect(ff,:),vHistCorrect(ff,:),'--g',bHistWrongFirst(ff,:),vHistWrongFirst(ff,:),'--r')
    subplot(1,3,2)
    hold on
    plot(cumProbWrongFirst(:,ff),cumProbCorrect(:,ff),'--k')
    subplot(1,3,3)
    hold on
    plot(trainday(task2list(ff)),aucClickDelayFirst(ff),'o','MarkerSize',sqrt(length(clickTimes{ff})),'Color',colTable(monkList2(ff),:))
    
end


for mm=(1:7)
    dd = trainDay2(monkList2==mm)';
    ww = rewardsNum(monkList2==mm)';
    rr = rewardsRate(monkList2==mm)';
    aa = aucClickDelay(monkList2==mm)';
    tt = clickTimeout(monkList2==mm)';
    rewardsRateRegr(mm,:) = (diag(ww)*[ones(size(dd)),dd])\(ww.*rr);
    aucClickDelayRegr(mm,:) = (diag(ww)*[ones(size(dd)),dd])\(ww.*aa);
    clickTimeoutRegr(mm,:) = (diag(ww)*[ones(size(dd)),dd])\(ww.*tt);
end


figure(11)
axis([0,plottimemax,0,length(task2list)+1])
set(gca,'YTick',1:length(legFields),'YTickLabel',legFields)
xlabel('Time (sec)')
ylabel('Session')

figure(12)
axis([0,max(timeMax),0,1])
legend(legFields)

figure(13)
hold on
for mm=(1:7)
    plot([min(trainday),max(trainday)],rewardsRateRegr(mm,1)+rewardsRateRegr(mm,2)*[min(trainday),max(trainday)],'Color',colTable(mm,:));
end
xlabel('Training day')
ylabel('Ratio correct')

figure(14)
hold on
for mm=(1:7)
    plot([min(trainday),max(trainday)],clickTimeoutRegr(mm,1)+clickTimeoutRegr(mm,2)*[min(trainday),max(trainday)],'Color',colTable(mm,:));
end
xlabel('Training day')
ylabel('Ratio timeout')

figure(15)
hold on
% errorbar(1:nbins,mean(norminv(rateCorrect,2),std(rateCorrect,[],2)./sqrt(length(task2list)),'k','LineWidth',4)
errorbar(1:nbins,normcdf(mean(min(max(norminv(rateCorrect),norminv(0.01)),norminv(0.99)),2)),std(rateCorrect,[],2)./sqrt(length(task2list)),'k','LineWidth',4)
xlabel('Time bin')
ylabel('Ratio correct')

figure(16)
hold on
% errorbar(1:nbins,mean(rateTimeout,2),std(rateTimeout,[],2)./sqrt(length(task2list)),'k','LineWidth',4)
errorbar(1:nbins,normcdf(mean(min(max(norminv(rateTimeout),norminv(0.01)),norminv(0.99)),2)),std(rateTimeout,[],2)./sqrt(length(task2list)),'k','LineWidth',4)
xlabel('Time bin')
ylabel('Ratio timeout')


figure(21)
legend(legFields)
hold on
plot(mean(bHist),mean(vHist),'k','LineWidth',4)
xlabel('Inter-clicks interval (sec)')
ylabel('Density')


figure(22)
subplot(1,3,1)
hold on
plot(mean(bHistCorrect),mean(vHistCorrect),'g',mean(bHistWrong),mean(vHistWrong),'r','LineWidth',4)
xlabel('Click-switch (sec)')
ylabel('Density')

subplot(1,3,2)
plot([0;mean(cumProbWrong,2)],[0;mean(cumProbCorrect,2)],'k','LineWidth',4)
axis([0,1,0,1])
xlabel('Cumul prob wrong click')
ylabel('Cumul prob correct click')

subplot(1,3,3)
hold on
for mm=(1:7)
    plot([min(trainday),max(trainday)],aucClickDelayRegr(mm,1)+aucClickDelayRegr(mm,2)*[min(trainday),max(trainday)],'Color',colTable(mm,:));
end
axis([min(trainday),max(trainday),0,1])
xlabel('Training day')
ylabel('AUC')


figure(23)
subplot(1,3,1)
hold on
plot(mean(bHistCorrect),mean(vHistCorrect),'g',mean(bHistWrongFirst),mean(vHistWrongFirst),'r','LineWidth',4)
xlabel('FIRST Click-switch (sec)')
ylabel('Density')

subplot(1,3,2)
plot([0;mean(cumProbWrongFirst,2)],[0;mean(cumProbCorrect,2)],'k','LineWidth',4)
axis([0,1,0,1])
xlabel('Cumul prob wrong click')
ylabel('Cumul prob correct click')

subplot(1,3,3)
hold on
% for mm=(1:7)
%     plot([min(trainday),max(trainday)],aucClickDelayRegr(mm,1)+aucClickDelayRegr(mm,2)*[min(trainday),max(trainday)],'Color',colTable(mm,:));
% end
axis([min(trainday),max(trainday),0,1])
xlabel('Training day')
ylabel('AUC')



