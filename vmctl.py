#!/usr/bin/env python
# coding: UTF-8

import sys
import yaml
import os.path
import pprint
from subprocess import Popen, PIPE, STDOUT

class ClusterConfig:
  u'''
  クラスタの設定ファイルの内容を格納するクラス。
  print_listメソッドを利用し、設定ファイルの内容を
  パースして出力できる。
  '''
  def __init__(self, config_name="cluster.yml"):
    self.config_name = config_name
    self.data = self.load_config()

  def load_config(self):
    if os.path.exists(self.config_name) == False:
      print "config file does not exit: %s" % self.config_name
      print ""
      print_usage()
      sys.exit(1)

    string = open(self.config_name).read()
    string = string.decode('utf8')
    return yaml.load(string)["clusters"]

  def print_list(self):
    u'''
    設定ファイルの内容をパースして一覧として表示する。
    '''

    print ""
    print "Available cluster"
    print "================="
    print "You can use the following cluster names."
    print ""
    for cluster in self.data:
      print "- %s:" % cluster["name"]
      description = "    " + cluster.get("description", "None description")
      print description

    print ""
    print "Cluster detail"
    print "=============="
    print "The following is the detail of each cluster."
    print ""
    print "Sample"
    print "------"
    print "Cluster: <cluster name>"
    print "  - <directory name>(<server list>)"
    print ""
    print "Clusters"
    print "--------"
    for cluster in self.data:
      print "Cluster: %s" % cluster["name"]
      for dir in cluster["dirs"]:
        servers = ""
        servers = ",".join(dir["servers"])
        print "  - %s(%s)" % (dir["name"], servers)
      print ""

class VMController:
  u'''
  VagrantのVMを管理するクラス。
  起動したり、停止したりできる。
  '''
  def __init__(self, cluster_config):
    self.cluster_config = cluster_config

  def start_vms(self, cluster_name):
    self.manage_vms(cluster_name, "up")
    
  def stop_vms(self, cluster_name):
    self.manage_vms(cluster_name, "halt")

  def manage_vms(self, cluster_name, action):
    u'''
    start_vmsメソッドやstop_vmsメソッドから呼ばれる
    汎用的なVM管理用メソッドである。
    '''
    for cluster in cluster_config.data:
      if cluster["name"] == cluster_name:
        for dir in cluster["dirs"]:
          os.chdir(os.path.join(sys.path[0], dir["name"]))
          for server in dir["servers"]:
            print action + " vm: " + server
            p = Popen("vagrant " + action + " " + server, shell=True, bufsize=1024,
                stdin=PIPE, stdout=PIPE, stderr=STDOUT)
            ret = p.wait()
            print p.communicate()[0].decode("utf8")
            print ""

def check_args(argv, argc):
  u'''
  引数の個数や内容を簡単に確認する。
  '''
  result = True

  if argc < 2:
    result = False
  else:
    if argv[1] == "up" or argv[1] == "halt":
      if argc < 3:
        result = False
    elif argv[1] != "list":
      result = False

  return result

def gen_cluster_config(argv, argc):
  u'''
  コマンドライン引数として設定ファイル名が
  渡されているかどうかを確認し、
  ClusterConfigのインスタンスを生成する。
  '''
  cluster_config = None

  if argv[1] == "up" or argv[1] == "halt":
    if argc == 3:
      cluster_config = ClusterConfig()
    elif argc == 4:
      cluster_config = ClusterConfig(sys.argv[3])
  else:
    if argc == 2:
      cluster_config = ClusterConfig()
    elif argc == 3:
      cluster_config = ClusterConfig(sys.argv[2])

  return cluster_config

def print_usage():
  print "Usage:"
  print "  %s up <cluster_name> [config_name]" % sys.argv[0]
  print "  %s halt <cluster_name> [config_name]" % sys.argv[0]
  print "  %s list [config_name]" % sys.argv[0]
  print ""
  print "Default config name:"
  print "  cluster.yml"

if __name__ == '__main__':
  argv = sys.argv
  argc = len(sys.argv)

  if check_args(argv, argc) == False:
    print_usage()
    sys.exit(1)

  cluster_config = gen_cluster_config(argv, argc)
  if cluster_config == None:
    print_usage()
    sys.exit(1)

  if argv[1] == "list":
    cluster_config.print_list()
    sys.exit(0)

  vm_controller = VMController(cluster_config)

  if argv[1] == "up":
    vm_controller.start_vms(argv[2])
  elif argv[1] == "halt":
    vm_controller.stop_vms(argv[2])

  sys.exit(0)

# vim: ft=python tw=0 sw=2 ts=2 et
