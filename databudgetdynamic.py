import matplotlib.pyplot as plt
import numpy as np
from dataclasses import dataclass
import random
import matplotlib.axes, matplotlib.figure
import matplotlib.patches as patches

OVERVIEW_HEIGHT = 0.4
ZOOM_HEIGHT = 0.8

colors : list[str] = [ # for each storage medium
    "#ccb2dd",
    "#6ebadd",
    "#fcc19c",
    "#a7e8a1"
]
source_color_index = 0
oh_color = '#969fa7'
used_color = '#ff730f'
med_colors = ['darkred', 'darkgreen', 'darkblue', 'darkviolet']
source_colors : dict[str,str] = {}
legend_handles : list[patches.Patch] = []

@dataclass(frozen=True)
class Source:
    type : str
    size : float

@dataclass(frozen=True)
class Medium:
    name : str
    total : float
    overhead : float
    sources : tuple
    color : str
    events : list[tuple[str,float]]
    max_rate : float

media : list[Medium] = []

media_count = int(input('Number of storage media: '))
if media_count == -1:
    print('DEBUG MODE') # for less tedious testing
    med_color_ind = random.randint(0, len(med_colors)-1)
    media = [
        Medium(name='First Med', total=13.24, overhead=1.1, color=med_colors[med_color_ind],
            events=[('Arm', 0), ("Boost", 1), ("Later", 0)], max_rate=1,
            sources=(
                Source(type='Video', size=2),
                Source(type='Sensor Data', size=7),
        )),
        Medium(name='Second Medium', total=128.9, overhead=2.3, color=med_colors[(med_color_ind+1)%len(med_colors)],
            events=[('Arm', 0), ("Boost", 1), ("Later", 2)], max_rate=2,
            sources=(
                Source(type='Video', size=35.17),
                Source(type='Sensor Data', size=15),
                Source(type='Logs', size=2),
        ))
    ]
    media_count = 0 # to skip media input loop
    source_colors = {
    "video":"#b886da",
    "sensor data":"#6ebadd",
    "logs":"#fcc19c"
    }
    for med in media: # add media to legend
        legend_handles.append(patches.Patch(color=med.color, label=med.name))
    for type, color in source_colors.items():  # add sources to legend
        legend_handles.append(patches.Patch(color=color,label=type))

for n in range(media_count): # get storage media information
    name = input(f'Medium {e+1} name: ')
    total_storage = float(input('\tTotal capacity (MB): '))
    over_head = float(input('\tFilesystem overhead (MB): '))
    source_count = int(input('\tNumber of data types: '))
    sources : list[Source] = []

    for m in range(source_count): # get source information
        source_name = input(f'\t\tMedium {n+1} Type {m+1} Name: ')
        source_size = float(input('\t\t\tSize (MB): '))

        if source_name.lower() not in source_colors.keys(): # if we haven't seen this source before,
            source_colors[source_name.lower()] = colors[source_color_index] # assign it a color
            legend_handles.append(patches.Patch(color=colors[source_color_index], label=source_name))
            source_color_index = (source_color_index + 1) % len(colors)
            if source_color_index == 0:
                print('More source types than colors.')
        sources.append(Source(source_name, source_size))

    this_color = med_colors[n % len(med_colors)] # color for this source
    legend_handles.append(patches.Patch(color=this_color, label=name))

    # get events for this medium
    events : list[tuple[str,float]] = []
    event_count = int(input(f'\tNumber of events for medium {n+1}: '))
    max_rate = -1

    for e in range(0, event_count):
        name = input(f'\t\tEvent {n+1} name: ')
        rate = float(input(f'\t\t{name} rate (MB/s): '))
        max_rate = max(max_rate, rate)
        events.append((name, rate))

    media.append(Medium(name, total_storage, over_head, tuple(sources), this_color, events, max_rate))

# set up figure
fig : matplotlib.figure.Figure = plt.figure()
fig.set_figwidth(4.8*(len(media)+0.5)) # additional half for legend
# print(fig.get_figheight())
subfigs : list[matplotlib.figure.SubFigure] = fig.subfigures(
    ncols=len(media)+1,
    width_ratios=([1] + [2]*len(media)),
    wspace=1
)

# drawing time
for n in range(len(media)):
    current_axes = subfigs[n+1].subplots( # n+1 to leave space for legend
        nrows=2,
        ncols=1,
        height_ratios=[2,1],
        #layout='constrained'
    )
    usage_ax : matplotlib.axes.Axes =  current_axes[0]
    event_ax : plt.Axes = current_axes[1]
    med : Medium = media[n]
    subfigs[n+1].suptitle(med.name, ha='left', x=0.1) 

    used = 0
    for s in med.sources:
        used += s.size
    free = med.total - used

    # create overall memory usage
    usage_ax.axis('off')
    usage_ax.barh([1], width=med.overhead, align='center', height=OVERVIEW_HEIGHT, color=oh_color, label='Filesystem Overhead')
    if med.overhead > 0.05:
        usage_ax.annotate(f'{med.overhead:.1f} MB', xy=(med.overhead/2, 1 + OVERVIEW_HEIGHT/2), ha='center', va='bottom')
    usage_ax.barh([1], width=used, left=med.overhead, height=OVERVIEW_HEIGHT, color=used_color)
    usage_ax.annotate(f'{used:.1f} MB', xy=(med.overhead + used/2, 1 + OVERVIEW_HEIGHT/2), ha='center', va='bottom')
    usage_ax.barh([1], width=med.total, color='none', edgecolor=med.color, height=OVERVIEW_HEIGHT)

    # add % used
    percent_used : float = (used+med.overhead)/med.total * 100.0
    if percent_used >= 2.0:
        arr = patches.FancyArrowPatch((0, 1+OVERVIEW_HEIGHT/2+0.4), (med.overhead+used, 1+OVERVIEW_HEIGHT/2+0.4),
                            arrowstyle='|-|,widthA=0.25,widthB=0.25', mutation_scale=20)
        usage_ax.add_patch(arr)
        usage_ax.annotate(f"{percent_used:.1f}% of {med.total:.1f} MB", (.5, 1.0), xycoords=arr, ha='center', va='bottom')
    else: # don't bother with bracket if too small
        usage_ax.annotate(f"{percent_used:.1f}%  used of {med.total:.1f} MB", xy=(med.total/2, 1+OVERVIEW_HEIGHT/2), xycoords='data', ha='center', va='bottom')

    # used space breakdown
    offset = 0
    for s in med.sources:
        s_width = s.size/used*med.total
        usage_ax.barh([0], width=s_width, align='center', left=offset, color=source_colors[s.type.lower()])
        usage_ax.annotate(f'{s.size:.1f} MB', xy=(offset + s_width/2, -ZOOM_HEIGHT/2), ha='center', va='top')
        offset += s_width

    # draw zoom-in lines
    zoom1 = patches.ConnectionPatch(xyA=(med.overhead, 1-OVERVIEW_HEIGHT/2), xyB=(0, ZOOM_HEIGHT/2), coordsA='data', color=med.color)
    usage_ax.add_artist(zoom1)
    zoom2 = patches.ConnectionPatch(xyA=(med.overhead+used, 1-OVERVIEW_HEIGHT/2), xyB=(med.total, ZOOM_HEIGHT/2), coordsA='data', color=med.color)
    usage_ax.add_artist(zoom2)

    # plot event rates for this medium
    events = med.events
    max_rate = med.max_rate
    x_labels = [ev[0] for ev in med.events]

    for n in range(len(events)): # draw rates
        ev_name, rate = events[n]
        event_ax.barh(0, width=1, height=ZOOM_HEIGHT*(rate/max_rate), left=n, color=med.color, align='edge')

    event_ax.set_xticks(np.arange(len(events)), x_labels)
    event_ax.set_yticks([]) # disable y-axis ticks
    event_ax.spines[['right','top']].set_visible(False)
    event_ax.set_xlim(right=len(events)+0.2)
    event_ax.set_ylim(top=1)
    arr = patches.FancyArrowPatch((len(events)+0.1, 0), (len(events)+0.1, ZOOM_HEIGHT),
                                arrowstyle='|-|,widthA=0.25,widthB=0.25', mutation_scale=20)
    event_ax.add_patch(arr)
    event_ax.annotate(f"{max_rate} MB/S", (.7, .5), xycoords=arr, ha='left', va='center')

# create legend
legend_handles.append(patches.Patch(color=oh_color, label='Filesystem\nOverhead'))
legend_handles.append(patches.Patch(color=used_color, label='Used'))
subfigs[0].legend(handles=legend_handles,loc='center right')

plt.show()
