#!/usr/bin/env python
# coding: UTF-8

import sys
import yaml
import os.path
import pprint
import argparse
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

  def print_list(self, verbose=False):
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

    if verbose == True:
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

  def print_runningvms(self, verbose=False):
    u'''
    現在動作しているVMを表示する
    '''
    print ""
    print "Running VMs"
    print "================="
    print ""
    p = Popen("VBoxManage list runningvms", shell=True, bufsize=1024,
        stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    ret = p.wait()
    print p.communicate()[0].decode("utf8")
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

  def status_vms(self, cluster_name):
    self.manage_vms(cluster_name, "status")

  def remove_vms(self, cluster_name):
    self.manage_vms(cluster_name, "destroy")

  def manage_vms(self, cluster_name, action):
    u'''
    start_vmsメソッドやstop_vmsメソッドから呼ばれる
    汎用的なVM管理用メソッドである。
    '''
    for cluster in cluster_config.data:
      if cluster["name"] == cluster_name:
        if action == "destroy":
          result = None
          while result != "y":
            result = raw_input("Do you realy want to destroy VMs? [y/n] : ")
            if result == "n":
              sys.exit(0)
          action = action + " -f"

        base_dir=os.getcwd()
        for dir in cluster["dirs"]:
          os.chdir(os.path.join(base_dir, dir["name"]))
          for server in dir["servers"]:
            print action + " vm: " + server
            p = Popen("vagrant " + action + " " + server, shell=True, bufsize=1024,
                stdin=PIPE, stdout=PIPE, stderr=STDOUT)
            ret = p.wait()
            print p.communicate()[0].decode("utf8")
            print ""

def parse_args():
  u'''
  コマンドライン引数とオプションを設定するメソッド。
  '''
  parser = argparse.ArgumentParser(description="The management tool for vagrant configs")
  parser.add_argument("command", choices=["up", "halt", "status", "destroy", "list", "rvms"], help="Which kind of task do you want to do")

  # listコマンドを使用するときは不要な引数なので、引数なしの時はデフォルト値を使用する
  parser.add_argument("cluster_name",
                      help="The name of cluster which you want to handle. When you execute \"list\" task, this argument is not necessary.",
                      default=None, nargs='?')

  parser.add_argument("-c","--config", help="The path of the configration of cluster. (default: ./cluster.yml)", type=file)
  parser.add_argument("-v", "--verbose", action="store_true", default=False, help="Enable verbose mode")
  args = parser.parse_args()
  return (parser, args)

if __name__ == '__main__':
  parser, args = parse_args()

  if args.config == None:
    cluster_config = ClusterConfig()
  else:
    cluster_config = ClusterConfig(args.config)

  if args.command == "list":
    cluster_config.print_list(args.verbose)
    sys.exit(0)
  elif args.command == "rvms":
    cluster_config.print_runningvms(args.verbose)
    sys.exit(0)
  elif args.cluster_name == None:
    u'''
    コマンドがlistでないときは、クラスタ名が必要
    このあたり、もう少しスマートに扱いたい
    '''
    print "ERROR: You need cluster_name"
    parser.print_usage()
    sys.exit(1)

  vm_controller = VMController(cluster_config)

  if args.command == "up":
    vm_controller.start_vms(args.cluster_name)
  elif args.command == "halt":
    vm_controller.stop_vms(args.cluster_name)
  elif args.command == "status":
    vm_controller.status_vms(args.cluster_name)
  elif args.command == "destroy":
    vm_controller.remove_vms(args.cluster_name)

  sys.exit(0)

# vim: ft=python tw=0 sw=2 ts=2 et
