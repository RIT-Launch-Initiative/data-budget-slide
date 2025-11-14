import matplotlib.pyplot as plt
import numpy as np
from dataclasses import dataclass
import random
import matplotlib.axes, matplotlib.figure
import matplotlib.patches as patches

OVERVIEW_HEIGHT = 0.4
ZOOM_HEIGHT = 0.8

colors : list[str] = [
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

media : list[Medium] = []

media_count = int(input('Number of storage media: '))
if media_count == -1:
    print('DEBUG MODE') # for less tedious testing
    med_color_ind = random.randint(0, len(med_colors)-1)
    media = [
        Medium(name='First Med', total=13.24, overhead=1.1, color=med_colors[med_color_ind], sources=(
            Source(type='Video', size=2),
            Source(type='Sensor Data', size=7)
        )),
        Medium(name='Second Medium', total=128.9, overhead=2.3, color=med_colors[(med_color_ind+1)%len(med_colors)], sources=(
            Source(type='Video', size=35.17),
            Source(type='Sensor Data', size=15),
            Source(type='Logs', size=2),
        ))
    ]
    media_count = 0
    source_colors = {
    "video":"#b886da",
    "sensor data":"#6ebadd",
    "logs":"#fcc19c"
    }
    for med in media:
        legend_handles.append(patches.Patch(color=med.color, label=med.name))
    for type, color in source_colors.items():
        legend_handles.append(patches.Patch(color=color,label=type))
for n in range(media_count):
    name = input(f'Medium {n+1} name: ')
    total_storage = float(input('\tTotal capacity (MB): '))
    over_head = float(input('\tFilesystem overhead (MB): '))
    source_count = int(input('\tNumber of data types: '))
    sources : list[Source] = []
    for m in range(source_count):
        source_name = input(f'\t\tMedium {n+1} Type {m+1} Name: ')
        source_size = float(input('\t\t\tSize (MB): '))
        if source_name.lower() not in source_colors.keys():
            source_colors[source_name.lower()] = colors[source_color_index]
            legend_handles.append(patches.Patch(color=colors[source_color_index], label=source_name))
            source_color_index = (source_color_index + 1) % len(colors)
            if source_color_index == 0:
                print('More source types than colors.')
        sources.append(Source(source_name, source_size))
    this_color = med_colors[n % len(med_colors)]
    legend_handles.append(patches.Patch(color=this_color, label=name))
    media.append(Medium(name, total_storage, over_head, tuple(sources), this_color))

# get events
events : list[tuple[str,dict[Medium,float]]] = [('', {})]
event_count = int(input('Number of events:'))
max_rate = -1
print('\tInitial rates:')
for med in media:
    rate = float(input(f'\t\t{med.name} (MB/s): '))
    events[0][1][med] = rate
    max_rate = max(max_rate, rate)
for n in range(1, event_count + 1):
    name = input(f'\tEvent {n} name:')
    events.append((name, {}))
    for med in media:
        rate = float(input(f'\t\t{med.name} (MB/s): '))
        events[n][1][med] = rate
        max_rate = max(max_rate, rate)

fig : matplotlib.figure.Figure
fig, (axes) = plt.subplots(
    ncols=1,
    nrows=len(media)+1,
    #layout='constrained'
)

for n in range(len(media)):
    usage_ax : matplotlib.axes.Axes = axes[n]
    med : Medium = media[n] 

    used = 0
    for s in med.sources:
        used += s.size
    free = med.total - used

    video = 1
    sensor = 2

    # create overall memory usage
    usage_ax.axis('off')
    if med.overhead != 0:
        usage_ax.barh([1], width=med.overhead, align='center', height=OVERVIEW_HEIGHT, color=oh_color, label='Filesystem Overhead')
        usage_ax.annotate(f'{med.overhead:.1f} MB', xy=(med.overhead/2, 1 + OVERVIEW_HEIGHT/2), ha='center', va='bottom')
    usage_ax.barh([1], width=used, left=med.overhead, height=OVERVIEW_HEIGHT, color=used_color)
    usage_ax.annotate(f'{used:.1f} MB', xy=(med.overhead + used/2, 1 + OVERVIEW_HEIGHT/2), ha='center', va='bottom')
    usage_ax.barh([1], width=med.total, color='none', edgecolor=med.color, height=OVERVIEW_HEIGHT)

    # add % used
    percent_used : float = (used+med.overhead)/med.total * 100.0
    arr = patches.FancyArrowPatch((0, 1+OVERVIEW_HEIGHT+0.4), (med.overhead+used, 1+OVERVIEW_HEIGHT+0.4),
                            arrowstyle='|-|,widthA=0.25,widthB=0.25', mutation_scale=20)
    usage_ax.add_patch(arr)
    usage_ax.annotate(f"{percent_used:.1f}% of {med.total:.1f} MB", (.5, 1.0), xycoords=arr, ha='center', va='bottom')

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

    # title it
    usage_ax.annotate(med.name, xy=(-0.1,0.5),xycoords='axes fraction', rotation=90, ha='center', va='center', size='large')

# plot event rates
event_ax : plt.Axes = axes[len(media)]
x_labels = [ev[0] for ev in events]
y_labels = [med.name for med in media]
for n in range(len(events)):
    ev_name, rates = events[n]
    for i in range(len(media)):
        rate = rates[media[i]]
        event_ax.barh([i+1], width=1, height=ZOOM_HEIGHT*(rate/max_rate), left=n, color=media[i].color, align='edge')
event_ax.set_xticks(np.arange(0,len(events)), x_labels)
event_ax.set_yticks(np.arange(1,len(media)+1), y_labels)
event_ax.spines[['right','top']].set_visible(False)
event_ax.set_xlim(right=len(events)+0.3)
event_ax.set_ylim(top=len(media)+1)
arr = patches.FancyArrowPatch((len(events)+0.1, 1), (len(events)+0.1, 1+ZOOM_HEIGHT),
                            arrowstyle='|-|,widthA=0.25,widthB=0.25', mutation_scale=20)
event_ax.add_patch(arr)
event_ax.annotate(f"{max_rate} MB/S", (.7, .5), xycoords=arr, ha='left', va='center')

# create legend
legend_handles.append(patches.Patch(color=oh_color, label='Filesystem\nOverhead'))
legend_handles.append(patches.Patch(color=used_color, label='Used'))
fig.legend(handles=legend_handles,loc='upper left', bbox_to_anchor=(0,0.9))
fig.subplots_adjust(left=0.35)

plt.show()