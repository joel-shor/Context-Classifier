% As an example, we will plot the activity of neuron #3 on tetrode #2,
% recorded during the 18:14:04 session on 10/25/2013 in rat #75

% FIRST, GO TO THE tetrodes DIRECTORY (on dropbox)

target_clust = 2;
wanted_sess = 60;

% Load the file for rat 75 containing session information
% This will load a variable called mux
load 'Data/Data Files/66.mat'

% Load the behavioral data for session 18:14:04 on day 10/25/2013
% This will load a variable called virmenLog
load 'Data/Data Files/VirmenLog/virmenLog66/20130807T092901.cmb.mat'

% Load spike information from tetrode #2
% This will load a variable called clust
load 'Data/Data Files/Clusters/clusters66/20130807T092901.cmb.4.mat'

% Locate the session we're interested in. In this case it's #83
mux.sessions(wanted_sess).name

format long;
% Determine the timestamp at which the recording was started
startTime = datenum(mux.sessions(wanted_sess).info.ObjInfo.InitialTriggerTime)

% Find all spikes belonging to neuron #3
s = clust.times(clust.identity==target_clust);

% Convert spike time to units of days (here, 31250 samples/sec is the
% sample rat ad 24*60*60 is the number of seconds per day)
s = s/31250/(24*60*60);

% Add spike time to the timestamp of the beginning of recording
s = s+startTime;

% Find the timestamps of behavioral data points using iterations
f = find(~isnan(virmenLog.iterations.number));
y = round(interp1(f,virmenLog.iterations.number(f),1:length(virmenLog.iterations.number)))

% Determine the iteration number at which each spike occured
sit = zeros(size(s));
for ndx = 1:length(sit)
    % Find the iteration preceding the spike
    f = find(virmenLog.iterations.time < s(ndx),1,'last')
    % Find the iteration following the spike
    g = find(virmenLog.iterations.time > s(ndx),1,'first');
    if ~isempty(f) && ~isempty(g)
        sit(ndx) = y(f);
    else % a spike occurs before the first or after the last iteration
        sit(ndx) = NaN;
    end
end
% Delete all spikes occuring before the first or after the last iteration
sit(isnan(sit)) = [];

dlmwrite('xs pre speed', virmenLog.position(1,sit))

% Determine the animal's running speed
speed = sqrt(sum(virmenLog.velocity.^2,1));

dlmwrite('speed arr', speed)

length(sit)

speed(33467)

% Leave only those spikes that occur when running is faster than 2 in/sec
f = find(speed > 2);
for ndx = length(sit):-1:1
    if isempty(find(f==sit(ndx),1))
        sit(ndx) = [];
    end
end

% Plot the animal's trajectory
plot(virmenLog.position(1,:),virmenLog.position(2,:),'k')
hold on

length(sit)

% Plot the spikes on top of the trajectory
plot(virmenLog.position(1,sit),virmenLog.position(2,sit),'r.')

dlmwrite('Animal 66, Session 60, Tetrode 4, Cluster 2, xs.validation', virmenLog.position(1,sit))
dlmwrite('Animal 66, Session 60, Tetrode 4, Cluster 2, ys.validation', virmenLog.position(2,sit))
