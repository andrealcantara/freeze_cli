import argparse
import configparser
import os.path
import subprocess
import sys
import logging
import traceback
import uuid


class PipFreezeCLI:
    CLI_VERSION = '1.0.0'
    INI_FILE = 'freeze.ini'

    def __load_ini_file(self, filename):
        full_path = os.path.abspath(os.path.join('./src', filename))
        path_config_lib = full_path if os.path.isfile(full_path) else \
            os.path.abspath(os.path.join(os.path.dirname(sys.executable), filename))
        self.config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
        if self.config.read(path_config_lib):
            logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                filename='freeze_info.log')
            return True
        else:
            logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                filename='freeze_error.log')
            logging.error("Não foi possível carregar o arquivo de configuração em {}".format(path_config_lib))
            return False

    def __init__(self):
        if self.__load_ini_file(self.INI_FILE):
            self.__run()

    def __run(self):
        self.parser = argparse.ArgumentParser(
            prog='Freeze-Cli',
            description='Gerencia ambientes de importacao de pip',
            epilog='Desenvolvido por: André Alcantara',
            usage='%(prog)s [options]'
        )
        self.parser.version = self.CLI_VERSION
        self.parser.add_argument("-v", '--version', action='version')
        self.parser.add_argument('-d', '--dev', action='store_true',
                                 help='Cria o arquivo no {} e o arquivo {} com a inclusão do arquivo dev.'.
                                 format(self.config['files']['dev'], self.config['main']['file']))
        self.parser.add_argument('-c', '--core', action='store_true',
                                 help='Cria o arquivo no {} e o arquivo {} com a inclusão do arquivo core.'.
                                 format(self.config['files']['core'], self.config['main']['file']))
        self.parser.add_argument('-a', '--all', action='store_true', help='Cria o arquivo no {}.'.
                                 format(self.config['files']['all']))
        self.parser.add_argument('--force', action='store_true', help='Adicionado juntamente com --dev ou --core, '
                                                                      'força a criação do arquivo como se nao '
                                                                      'houvesse o outro, adicionando todo o '
                                                                      'pip-freeze nele.')

        parser_args = None
        try:
            # parser_args = self.parser.parse_known_args()
            parser_args = self.parser.parse_args()
            self.__createfolder()
            if len(sys.argv) > 1:
                is_forced = parser_args.force
                if parser_args.dev:
                    self.__generate_dev(is_forced)
                elif parser_args.core:
                    self.__generate_core(is_forced)
                elif parser_args.all:
                    self.__generate_all()
                self.__generate_local_requeriments()
            else:
                self.parser.print_help()
                sys.exit(1)
        except argparse.ArgumentError as e:
            print("Argumento inválido {}".format(sys.argv[1:][0]))
            print(e)
            sys.exit(1)

    def __createfolder(self):
        if not os.path.isdir(self.config['main']['config']):
            subprocess.run('mkdir -p ' + self.config['main']['config'], shell=True, capture_output=True)

    def __generate_dev(self, is_forced):
        logging.info('Inciando freeze dev')
        self.__freeze_another(target_req=self.config['files']['dev'], compare_req=self.config['files']['core'],
                              has_force=is_forced)
        logging.info('Finalizado freeze')
        logging.info('Criado arquivo {}'.format(self.config['files']['dev']))

    def __generate_core(self, is_forced):
        logging.info('Inciando freeze core')
        self.__freeze_another(target_req=self.config['files']['core'], compare_req=self.config['files']['dev'],
                              has_force=is_forced)
        logging.info('Finalizado freeze')
        logging.info('Criado arquivo {}'.format(self.config['files']['core']))

    def __generate_all(self):
        logging.info('Inciando freeze all')
        self.__freeze_another(target_req=self.config['files']['all'])
        logging.info('Finalizado freeze')
        logging.info('Criado arquivo {}'.format(self.config['files']['all']))

    def __freeze_another(self, target_req='', compare_req='-h', has_force=False):
        pip_all = subprocess.check_output(self.config['command']['pip'], shell=True).decode().split('\n')
        pip_all = sorted(set(pip_all))
        other_freeze = None
        if has_force:
            logging.info("*** Forced ***")
        if os.path.isfile(compare_req) != has_force:
            other_freeze = subprocess.run(self.config['command']['cat']
                                          .format(compare_req), shell=True, capture_output=True)
            if other_freeze.stderr:
                other_freeze = None
            else:
                other_freeze = other_freeze.stdout

        if other_freeze:
            freeze_split = other_freeze.decode().split('\n')
            freeze_split = sorted(set(freeze_split))
            result = [item for item in pip_all if item not in freeze_split]
        else:
            result = set(pip_all)
        with open(target_req, 'a+') as req:
            req.seek(0)
            req.truncate()
            for line in result:
                if line:
                    req.write(line)
                    req.write('\n')

    def __generate_local_requeriments(self):
        exist_dev = os.path.isfile(self.config['files']['dev'])
        exist_core = os.path.isfile(self.config['files']['core'])
        result = []
        if exist_core:
            result.append('-r {}'.format(self.config['files']['core']))
        if exist_dev:
            result.append('-r {}'.format(self.config['files']['dev']))
        logging.info("Iniciando o {}".format(self.config['main']['file']))
        logging.info("Core_File_Exist: {}, Dev_File_Exist: {}".format(exist_core, exist_dev))
        with open(self.config['main']['file'], 'a+') as file:
            file.seek(0)
            file.truncate()
            for line in result:
                file.write("{}\n".format(line))
        logging.info('Criado/Atualizado o arquivo {}'.format(self.config['main']['file']))
