#!/usr/bin/env python3

import datetime
import gzip
import random
import pytz

def syslog_generator(timestamps):
    hostnames = ["localhost"]
    processes = ["apt-get", "auditd", "avahi-daemon", "bluetoothd", "clamd", "cron", "cupsd", "dbus-daemon", "dhclient", "fail2ban", "firewalld", "fluentd", "gdm", "httpd", "iptables", "kernel", "logrotate", "logwatch", "monit", "nagios", "named", "nfsd", "nginx", "ntpd", "openldap", "openvpn", "polkitd", "postgres", "prometheus", "redis", "rsyslog", "samba", "snmpd", "sshd", "sssd", "strongswan", "udevd", "xorg", "zabbix", "zookeeper"]
    cron_jobs = ["backup.sh", "cleanup.sh", "update.sh", "sync.sh", "monitor.sh", "deploy.sh", "restart.sh", "check.sh", "scan.sh", "report.sh", "archive.sh", "compress.sh", "extract.sh", "move.sh", "copy.sh", "delete.sh", "create.sh", "init.sh", "shutdown.sh", "start.sh", "stop.sh", "reload.sh", "refresh.sh", "reboot.sh", "upgrade.sh", "downgrade.sh", "install.sh", "uninstall.sh", "configure.sh", "build.sh", "test.sh", "validate.sh", "verify.sh", "clean.sh", "purge.sh", "backup_db.sh", "restore_db.sh", "migrate.sh", "seed.sh", "generate.sh", "fetch.sh", "pull.sh", "push.sh", "commit.sh", "merge.sh", "rebase.sh", "tag.sh", "branch.sh", "checkout.sh"]
    oom_processes = ["apache2", "mysqld", "java", "python", "node", "ruby", "php", "perl", "go", "rust", "dotnet", "mono", "nginx", "postgres", "redis", "memcached", "elasticsearch", "logstash", "kibana", "hadoop", "spark", "hbase", "cassandra", "zookeeper", "kafka", "storm", "flink", "beam", "airflow", "druid", "presto", "trino", "clickhouse", "influxdb", "timescaledb", "prometheus", "grafana", "telegraf", "zabbix", "icinga", "nagios", "openvpn", "strongswan", "openldap", "samba", "nfsd", "glusterfs", "ceph", "minio", "consul", "vault"]
    dhcp_interfaces = ["eth0", "eth1", "wlan0", "wlan1", "eth2", "eth3", "eth4", "eth5", "eth6", "eth7", "eth8", "eth9", "eth10", "eth11", "eth12", "eth13", "eth14", "eth15", "eth16", "eth17", "eth18", "eth19", "eth20", "eth21", "eth22", "eth23", "eth24", "eth25", "eth26", "eth27", "eth28", "eth29", "eth30", "eth31", "eth32", "eth33", "eth34", "eth35", "eth36", "eth37", "eth38", "eth39", "eth40", "eth41", "eth42", "eth43", "eth44", "eth45", "eth46", "eth47"]
    apt_packages = ["libc6", "openssl", "bash", "coreutils", "vim", "nano", "emacs", "git", "curl", "wget", "tar", "gzip", "bzip2", "xz-utils", "zip", "unzip", "rsync", "openssh-client", "openssh-server", "net-tools", "iproute2", "dnsutils", "bind9", "apache2", "nginx", "mysql-server", "postgresql", "redis-server", "memcached", "mongodb", "rabbitmq-server", "kafka", "zookeeper", "docker-ce", "helm", "prometheus", "zabbix-agent", "icinga2", "nagios-nrpe-server", "openvpn", "strongswan", "openldap", "samba", "nfs-kernel-server"]

    for ts in timestamps:
        timestamp_str = ts.strftime("%b %d %H:%M:%S")
        hostname = random.choice(hostnames)
        process = random.choice(processes)

        if process == "ntpd" and (random.random() < 0.999 or ts.year < 2016):
            continue

        if process == "named" and random.random() < 0.97:
            continue

        if process == "cron":
            job = random.choice(cron_jobs)
            message = f"({job}) FAILED (exit status {random.randint(1, 127)})"
            pid = random.randint(1000, 39999)
            yield f"{timestamp_str} {hostname} {process}[{pid}]: {message}"

        elif process == "apt-get":
            pkg = random.choice(apt_packages)
            message = f"Installed: {pkg} ({random.randint(1,3)}.{random.randint(0,9)}-{random.randint(1,20)})"
            pid = random.randint(1000, 39999)
            yield f"{timestamp_str} {hostname} {process}[{pid}]: {message}"

        elif process == "dhclient":
            iface = random.choice(dhcp_interfaces)
            ip = f"192.168.{random.randint(0,255)}.{random.randint(2,254)}"
            message = f"DHCPREQUEST on {iface} to 255.255.255.255 port 67 interval {random.randint(3,10)}"
            yield f"{timestamp_str} {hostname} {process}: {message}"
            message = f"DHCPACK from 192.168.{random.randint(0,255)}.1 ({ip})"
            yield f"{timestamp_str} {hostname} {process}: {message}"
            message = f"bound to {ip} -- renewal in {random.randint(300,7200)} seconds."
            yield f"{timestamp_str} {hostname} {process}: {message}"

        elif process == "docker":
            pid = random.randint(1000, 39999)
            container_id = ''.join(random.choices('abcdef0123456789', k=12))
            message = f"Container {container_id} started"
            yield f"{timestamp_str} {hostname} {process}[{pid}]: {message}"

        elif process == "dovecot":
            pid = random.randint(1000, 39999)
            user = random.choice(users)
            message = f"imap-login: Login: user=<{user}>, method=PLAIN, rip={random.randint(10,250)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}, lip=192.168.1.1, mpid={pid}, TLS"
            yield f"{timestamp_str} {hostname} {process}: {message}"

        elif process == "httpd":
            pid = random.randint(1000, 39999)
            message = f"caught SIGTERM, shutting down"
            yield f"{timestamp_str} {hostname} {process}[{pid}]: {message}"

        elif process == "kernel":
            oom_proc = random.choice(oom_processes)
            pid = random.randint(1000, 39999)
            message = f"Out of Memory: Killed process {pid} ({oom_proc})."
            yield f"{timestamp_str} {hostname} {process}: {message}"

        elif process == "mysql":
            pid = random.randint(1000, 39999)
            message = f"ready for connections. Version: '5.7.31'  socket: '/var/run/mysqld/mysqld.sock'  port: 3306  MySQL Community Server (GPL)"
            yield f"{timestamp_str} {hostname} {process}[{pid}]: {message}"

        elif process == "named":
            pid = random.randint(1000, 39999)
            message = f"zone in-addr.arpa/IN: loaded serial {ts.year}{ts.month:02d}{ts.day:02d}{ts.hour:02d}"
            yield f"{timestamp_str} {hostname} {process}[{pid}]: {message}"

        elif process == "ntpd":
            pid = random.randint(1000, 39999)
            message = f"time reset by step to {ts.year}-{ts.month:02d}-{ts.day:02d} {ts.hour:02d}:{ts.minute:02d}:{ts.second:02d} (offset {random.uniform(-0.5, 0.5):.6f} sec)"
            yield f"{timestamp_str} {hostname} {process}[{pid}]: {message}"

        elif process == "postfix":
            pid = random.randint(1000, 39999)
            message = f"connect from unknown[{random.randint(10,250)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}]"
            yield f"{timestamp_str} {hostname} {process}[{pid}]: {message}"

        elif process == "sshd":
            pid = random.randint(1000, 39999)
            ip = f"{random.randint(10,250)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
            users = ["alice", "bob", "charlie", "dave", "eve", "frank", "grace", "heidi", "ivan", "judy", "karl", "louis", "mallory", "nancy", "oscar", "peggy", "quincy", "rachel", "sam", "trent", "ursula", "victor", "walter", "xander", "yvonne", "zach", "amy", "brian", "carl", "diana", "edward", "fiona", "george", "hannah", "ian", "jessica", "kevin", "laura", "michael", "nina", "oliver", "paul", "quinn", "rebecca", "steve", "tina", "uma", "vincent", "wendy", "xavier", "yasmine", "zoe", "juan", "maria", "carlos", "sofia", "lucas", "valentina", "martin", "camila"]
            user = random.choice(users)
            message = f"Accepted password for {user} from {ip} port {random.randint(1024,65535)} ssh2"
            yield f"{timestamp_str} {hostname} {process}[{pid}]: {message}"
        
        elif process == "auditd":
            pid = random.randint(1000, 39999)
            message = f"audit: type=1400 audit(1617211200.000:1000): auid=4294967295 uid=0 gid=0 ses=4294967295 subj=system_u:system_r:unconfined_service_t:s0-s0:c0.c1023 msg='op=PAM:authentication acct=\"\" exe=\"/usr/sbin/sshd\" hostname=? addr=? terminal=? res=1'"
            yield f"{timestamp_str} {hostname} {process}[{pid}]: {message}"

        elif process == "monit":
            pid = random.randint(1000, 39999)
            message = f"Monit instance failed to start due to configuration error"
            yield f"{timestamp_str} {hostname} {process}[{pid}]: {message}"

        elif process == "sssd":
            pid = random.randint(1000, 39999)
            message = f"SSSD service crashed unexpectedly with signal {random.choice([6, 11, 15])}"
            yield f"{timestamp_str} {hostname} {process}[{pid}]: {message}"

        elif process == "udevd":
            pid = random.randint(1000, 39999)
            message = f"Failed to rename network interface from eth0 to ens33 due to permission denied"
            yield f"{timestamp_str} {hostname} {process}[{pid}]: {message}"

        elif process == "nfsd":
            pid = random.randint(1000, 39999)
            message = f"client {random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)} connection timed out"
            yield f"{timestamp_str} {hostname} {process}[{pid}]: {message}"

        elif process == "xorg":
            pid = random.randint(1000, 39999)
            message = f"(EE) {random.choice(['Segmentation fault at address 0x0', 'Failed to initialize core devices'])}"
            yield f"{timestamp_str} {hostname} {process}[{pid}]: {message}"

        elif process == "firewalld":
            pid = random.randint(1000, 39999)
            message = f"Firewall failed to reload: {random.choice(['invalid rule detected', 'missing configuration file'])}"
            yield f"{timestamp_str} {hostname} {process}[{pid}]: {message}"

        elif process == "postgres":
            pid = random.randint(1000, 39999)
            message = f"database system encountered an unexpected shutdown"
            yield f"{timestamp_str} {hostname} {process}[{pid}]: {message}"

        elif process == "bluetoothd":
            pid = random.randint(1000, 39999)
            message = f"Bluetooth management interface failed to initialize due to missing firmware"
            yield f"{timestamp_str} {hostname} {process}[{pid}]: {message}"

        elif process == "zabbix":
            pid = random.randint(1000, 39999)
            message = f"Zabbix agent failed to start: configuration file error"
            yield f"{timestamp_str} {hostname} {process}[{pid}]: {message}"

        elif process == "clamd":
            pid = random.randint(1000, 39999)
            message = f"Virus database update failed: checksum mismatch detected."
            yield f"{timestamp_str} {hostname} {process}[{pid}]: {message}"

        elif process == "nginx":
            pid = random.randint(1000, 39999)
            message = f"Configuration reloaded successfully, worker process {pid} running smoothly."
            yield f"{timestamp_str} {hostname} {process}[{pid}]: {message}"

        elif process == "avahi-daemon":
            pid = random.randint(1000, 39999)
            message = f"Error: Failed to resolve host name for {random.randint(10,250)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}."
            yield f"{timestamp_str} {hostname} {process}[{pid}]: {message}"

        elif process == "rsyslog":
            pid = random.randint(1000, 39999)
            message = f"rsyslogd started, monitoring system logs."
            yield f"{timestamp_str} {hostname} {process}[{pid}]: {message}"

        elif process == "redis":
            pid = random.randint(1000, 39999)
            message = f"Redis server {pid} encountered a memory allocation error."
            yield f"{timestamp_str} {hostname} {process}[{pid}]: {message}"

        elif process == "logrotate":
            if random.random() < 0.95:
                continue
            pid = random.randint(1000, 39999)
            message = f"Log rotation completed successfully for /var/log/syslog."
            yield f"{timestamp_str} {hostname} {process}[{pid}]: {message}"

        elif process == "zookeeper":
            pid = random.randint(1000, 39999)
            message = f"Zookeeper node {pid} is now the leader."
            yield f"{timestamp_str} {hostname} {process}[{pid}]: {message}"

        elif process == "iptables":
            pid = random.randint(1000, 39999)
            message = f"Error: Failed to apply rule due to syntax error."
            yield f"{timestamp_str} {hostname} {process}[{pid}]: {message}"

        elif process == "fail2ban":
            pid = random.randint(1000, 39999)
            message = f"Unbanned IP {random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)} after timeout."
            yield f"{timestamp_str} {hostname} {process}[{pid}]: {message}"

        elif process == "gdm":
            pid = random.randint(1000, 39999)
            message = f"GDM session ended unexpectedly, attempting restart."
            yield f"{timestamp_str} {hostname} {process}[{pid}]: {message}"

        elif process == "polkitd":
            pid = random.randint(1000, 39999)
            message = f"Authentication Agent for unix-process:{pid} successfully deregistered."
            yield f"{timestamp_str} {hostname} {process}[{pid}]: {message}"

        elif process == "dbus-daemon":
            pid = random.randint(1000, 39999)
            message = f"Failed to activate service 'org.freedesktop.systemd1': timeout expired."
            yield f"{timestamp_str} {hostname} {process}[{pid}]: {message}"

        elif process == "samba":
            pid = random.randint(1000, 39999)
            message = f"smbd version 4.10.16 stopped due to unexpected error."
            yield f"{timestamp_str} {hostname} {process}[{pid}]: {message}"

        elif process == "snmpd":
            pid = random.randint(1000, 39999)
            message = f"Received SNMP request from {random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}."
            yield f"{timestamp_str} {hostname} {process}[{pid}]: {message}"

        elif process == "cupsd":
            pid = random.randint(1000, 39999)
            message = f"Printer queue cleared successfully."
            yield f"{timestamp_str} {hostname} {process}[{pid}]: {message}"

        elif process == "logwatch":
            pid = random.randint(1000, 39999)
            message = f"Logwatch 1.1.4 completed analysis, no issues found."
            yield f"{timestamp_str} {hostname} {process}[{pid}]: {message}"

        elif process == "strongswan":
            pid = random.randint(1000, 39999)
            message = f"charon (strongSwan 0.8.9) encountered a certificate validation error."
            yield f"{timestamp_str} {hostname} {process}[{pid}]: {message}"

        elif process == "nagios":
            pid = random.randint(1000, 39999)
            message = f"Nagios 4.4.6 completed system check, all services operational."
            yield f"{timestamp_str} {hostname} {process}[{pid}]: {message}"

        elif process == "openldap":
            pid = random.randint(1000, 39999)
            message = f"slapd {pid} stopped due to configuration error."
            yield f"{timestamp_str} {hostname} {process}[{pid}]: {message}"

        elif process == "fluentd":
            pid = random.randint(1000, 39999)
            message = f"Fluentd worker {pid} encountered a buffer overflow."
            yield f"{timestamp_str} {hostname} {process}[{pid}]: {message}"

        elif process == "prometheus":
            pid = random.randint(1000, 39999)
            message = f"Prometheus scrape interval adjusted to 15s."
            yield f"{timestamp_str} {hostname} {process}[{pid}]: {message}"

        elif process == "openvpn":
            pid = random.randint(1000, 39999)
            message = f"OpenVPN {pid} connection established successfully."
            yield f"{timestamp_str} {hostname} {process}[{pid}]: {message}"

        else:
            raise ValueError(f"Unknown process: {process}")

def timestamps():
    unixtime = 915000000
    while unixtime < 1741390000:
        yield datetime.datetime.fromtimestamp(unixtime, tz=pytz.UTC).astimezone(pytz.timezone("America/Argentina/Tucuman"))
        unixtime += random.randint(0, 900)

random.seed(8888)
logs = syslog_generator(timestamps())
logs = list(logs)

with gzip.open("../attachments/syslog.gz", "wt") as f:
    for log_entry in logs:
        f.write(log_entry + "\n")
