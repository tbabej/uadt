import os
import glob
import subprocess

from joblib import Parallel, delayed

CURRENT_MARKS = 28


def split_file(marks_filename):
    pcap_filename = marks_filename.split('.')[0] + '.pcap'

    print("Processing {}".format(pcap_filename))

    with open(marks_filename) as marks_f:
        marklines = list(marks_f.readlines())
        marks_num = len(marklines)

    if marks_num != CURRENT_MARKS:
        print("Invalid number of marks, skipping.")

    for mark_index in range(marks_num/2):
        start_line = marklines[2*mark_index]
        end_line = marklines[2*mark_index+1]

        start_line_parts = start_line.split(' ')
        end_line_parts = end_line.split(' ')

        start_timestamp = ' '.join(start_line_parts[:2])
        end_timestamp = ' '.join(end_line_parts[:2])

        event_name = '_'.join(start_line_parts[-1].strip().split('_')[1:])

        query = 'frame.time >= "{0}" and frame.time <= "{1}"'.format(
            start_timestamp,
            end_timestamp
        )

        # Generate the name for the output file
        time_suffix = end_timestamp.replace('-','')
        time_suffix = time_suffix.replace(':', '')
        time_suffix = time_suffix.replace(' ', '_').split('.')[0]

        output_filename = os.path.join(
                'data_split',
                event_name + '_' + time_suffix + '.pcap'
        )

        if os.path.exists(output_filename):
            # This should not happen due to the fact that two events do not
            # happen at the same time
            output_filename = output_filename.split('.')[0] + '_1.pcap'

        retcode = subprocess.call([
            'tshark',
            '-r', pcap_filename,
            '-w', output_filename,
            query])

        if retcode != 0:
            print("Extraction of {0} unsuccessful".format(event_name))


Parallel(n_jobs=4)(delayed(split_file)(marks_filename) for marks_filename in glob.glob('data/*.marks'))
