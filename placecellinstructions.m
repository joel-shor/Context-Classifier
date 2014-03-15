% As an example, we will plot the activity of neuron #3 on tetrode #2,
% recorded during the 18:14:04 session on 10/25/2013 in rat #75

% FIRST, GO TO THE tetrodes DIRECTORY (on dropbox)

% Load the file for rat 75 containing session information
% This will load a variable called mux
load 75.mat

% Load the behavioral data for session 18:14:04 on day 10/25/2013
% This will load a variable called virmenLog
load virmenLog75\20131025T181404.cmb.mat

% Load spike information from tetrode #2
% This will load a variable called clust
load clusters75\20131025T181404.cmb.2.mat

% Locate the session we're interested in. In this case it's #83
mux.sessions(83).name

% Determine the timestamp at which the recording was started
startTime = datenum(mux.sessions(83).info.ObjInfo.InitialTriggerTime);

% Find all spikes belonging to neuron #3
s = clust.times(clust.identity==3);

% Convert spike time to units of days (here, 31250 samples/sec is the
% sample rat ad 24*60*60 is the number of seconds per day)
s = s/31250/(24*60*60);

% Add spike time to the timestamp of the beginning of recording
s = s+startTime;

% Find the timestamps of behavioral data points using iterations
f = find(~isnan(virmenLog.iterations.number));
y = round(interp1(f,virmenLog.iterations.number(f),1:length(virmenLog.iterations.number)));

% Determine the iteration number at which each spike occured
sit = zeros(size(s));
for ndx = 1:length(sit)
    % Find the iteration preceding the spike
    f = find(virmenLog.iterations.time < s(ndx),1,'last');
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

% Determine the animal's running speed
speed = sqrt(sum(virmenLog.velocity.^2,1));

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

% Plot the spikes on top of the trajectory
plot(virmenLog.position(1,sit),virmenLog.position(2,sit),'r.')