# About

This repository is to research the potential of different compression algorithms to deflate the size of files 
in JSON formats and linux system logs.

The first ones typically look like this (EOL-separated JSON lines)
```shell
{"timestamp": "2023-01-08T17:51:22.817Z", "temperature": 5.072506100990818, "rad_direct_horizontal": -2.610169876576805, "rad_diffuse_horizontal": -6.192455990847108, "type": "global", "country": "Canada", "hashcode": 981341}
{"timestamp": "2023-01-08T17:51:22.890Z", "temperature": -0.5939279563427782, "rad_direct_horizontal": 6.686203948512087, "rad_diffuse_horizontal": -9.78597625469231, "type": "global", "country": "Australia", "hashcode": 422994}
```

and the specimen of the second ones can be found in the `/var/log` directory and subdirectory, here is an example:

```shell
Jan  7 13:05:12 system systemd[985]: Reached target Sockets.
Jan  7 13:05:12 system systemd[985]: Reached target Basic System.
Jan  7 13:05:12 system systemd[1]: Started User Manager for UID 125.
Jan  7 13:05:12 system systemd[985]: Starting Sound Service...
and so on
```

In general, these logs have much higher entropy than Standard English text (which usually falls somewhere between 3.5 and 5.0)
And due to this very fact these logs can be compressed the most using a dictionary-based family of compression algorithms (LZ*)

My aim was to find not only the best compression algorithm, but also memory- and cpu-wise. In addition, it has to have
a wide support across different platforms and languages. 

As the initial list I took [this one](http://mattmahoney.net/dc/text.html),
which comprises 200+ different archivers. Unfortunately, the best ones are highly experimental and don't quite suite my needs
(I need stable, production-ready OSS with small development and maintenance overhead).

After some considerations and experiments I have shortlisted the following ones: `zstd`, `brotli`, `xz` and `gzip` 
(the latter one for reference only since it's a long-term standard in lossless compression).

zstd installation

```shell
sudo apt install zstd
```
brotli installation

```shell
sudo apt install brotli
```

`xz` is included into most linux distributive by default

# Testing methodology

The test logs were generated using python script:

```shell
python3 sample_generator.py -s table_schema_v1.json -l 1000000 -o test.txt
```

And then each archiver was run with different set of flags, using standard linux tools to measure run time and memory 
consumption, like this:

```shell
/usr/bin/time -v brotli -q 10 -w 10 test.txt
```

The Table 1 summarizes the averages for the optimum on each archiver, optimisation function is:

```shell
score = opt(compressed_size, run_time, mem_consumption)
```

The score is bigger if compressed_size is _smaller_ (this is included to final score with the biggest weight)

The score is bigger if run_time is _smaller_ (if run_time > 10x for `gzip`, the score for this part quickly falls to 0)

The score is bigger if mem_consumption is _smaller_

(Note the big deviation for zstd, which means this archiver has to be tested with different set of flags, since increasing
the complexity of compression algorithm dramatically increases the compression time and affects the score):

### Table 1

| input file size, MB (lines) | algorithm | flags       | run time  | peak mem consumption, kbytes | compressed size, MB |
|-----------------------------|-----------|-------------|-----------|------------------------------|---------------------|
| 220 (1M)                    | brotli    | -q 10 -w 10 | 1:24.79   | 6152                         | 34.0                |
| 220 (1M)                    | zstd      | -11         | 0:21.59   | 96092                        | 40.0                |
| 220 (1M)                    | zstd      | -18         | 2:36.10   | 188752                       | 33.3                |
| 220 (1M)                    | xz        | -6          | 2:41.48   | 84484                        | 32.6                |
| 220 (1M)                    | gzip      | -6          | 0:08.37   | 2164                         | 42.4                |

# Strategy to choose the optimal archiver

If there are memory constraints, then the archivers have to be considered in the following order:

```shell
brotli
gzip
```

Many advanced archivers have a very big memory footprint, not always configurable via flags.

If there are no memory constraints, or they are relaxed, then the archivers have to be considered in the following order:

```shell
xz
brotli
zstd
gzip
```

# References

## zstd

[1] http://facebook.github.io/zstd/

[2] https://raw.githack.com/facebook/zstd/release/doc/zstd_manual.html

[3] https://github.com/facebook/zstd

[4] https://github.com/facebook/zstd/releases/tag/v1.1.3

[5] https://github.com/luben/zstd-jni (java support via JNI)

## brotli

[6] https://github.com/google/brotli

[7] https://github.com/nixxcode/jvm-brotli (port)

[8] https://github.com/hyperxpro/Brotli4j (java support via JNI)

## xz

[9] https://tukaani.org/xz/java.html (port)

## full list + including experimental archivers (less supported/academic projects)

[10] http://mattmahoney.net/dc/text.html

## Misc

[11] https://github.com/vkrasnov/dictator (generating custom dictionaries)



