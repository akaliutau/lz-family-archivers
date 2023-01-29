import argparse
from pathlib import Path

from process import Process

archivers = {
    'gzip': {
        'compression_levels': 9,
        'ext': '.gz'
    },
    'zstd': {
        'compression_levels': 18,
        'ext': '.zst'
    },
    'xz': {
        'compression_levels': 9,
        'ext': '.xz'
    },
    'brotli': {
        'compression_levels': 9,
        'ext': '.br'
    }
}

archivers_to_test = ['gzip', 'zstd', 'xz', 'brotli']

columns = ['compression_level', 'original_size', 'compressed_size', 'ratio', 'runtime_sec', 'mem_peak_mb']

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Runs benchmark for selected archivers')
    parser.add_argument('-i', '--input_file', help='test file', required=True)

    args = parser.parse_args()

    input_file = args.input_file
    test_file = 'test.dat'
    output_file_suffix = '_test.csv'
    original_size = Path(input_file).stat().st_size

    for archiver in archivers_to_test:
        print('testing %s' % archiver)
        report = list()
        report.append(','.join(columns) + '\n')
        for compression_level in range(archivers.get(archiver).get('compression_levels') - 1):
            level = compression_level + 1
            command = [archiver, '-k', '-f', '-' + str(level), input_file]
            pr = Process(command)
            pr.exec()
            while pr.await_completion():
                pass
            stat = pr.get_statistics()
            output_file = input_file + archivers.get(archiver).get('ext')
            compressed_size = Path(output_file).stat().st_size
            res = [
                level,
                original_size,
                compressed_size,
                original_size / compressed_size,
                stat['run_time_sec'],
                stat['max_rss_memory_mb'],
            ]
            report.append(','.join([str(c) for c in res]) + '\n')
            print(pr.get_statistics())
        with open(archiver + output_file_suffix, 'w+') as f:
            f.writelines(report)
