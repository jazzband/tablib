


from helpers import *
# from core import Parse

from packages import opster



opts = (
	('v', 'version', False, 'Report tabbed version'),
	('', 'nsanity_xsd', 'resources/nsanity_schema.xsd', 'schema doc (.xsd) used to validate nsantity files'),
	('', 'nsanity_files', 'False', 'list of nsanity files or directories containing nsanity files'),
	('', 'emcgrab_files', 'False', 'name of file to write process ID to'),
	('d', 'debug', False, 'Enable debug mode')
)


@opster.command(options=opts, usage='[-d] [--nsanity_files DIR]')
def start(**opts):
	"""Parses """
	
	# print opts
	opts = Object(**opts)
	
	# print('%sNetApp nSANity MigrationParser' % Fore.YELLOW)
	if opts.debug:
		log.debug_mode = True
	
	if opts.validate_nsanity and not opts.nsanity_xsd:
		print('Please provide the nsanity schema to validate against (--nsanity_xsd=command_output.xsd) .')

		exit(1)
	
	if not opts.nsanity_files and not opts.emcgrab_files:
		print('Please provide input files to parse.')
		
		exit(1)	   
	
	nsanity_extensions = ('.xml', '.gz')
		
	parser = Parse(nsanity_xsd=opts.nsanity_xsd)
	
	for path in opts.nsanity_files.split(','):
		
		entry = os.path.abspath(path)
		
		if not os.path.exists(entry):
			log.critical('path does not exist [%s]' % (entry))
			continue
		
		if os.path.isdir(entry):
			for root, dirs, files in os.walk(entry):
				for name in files:
					file = os.path.join(root, name)
					if file.endswith(nsanity_extensions):
						parser.nsanity_file_paths.append(file)
					else:
						log.debug('skipping %s, does not have valid extension (.xml or .gz)' % file)
		else:
			if entry.endswith(nsanity_extensions):
				file = os.path.abspath(entry)
				parser.nsanity_file_paths.append(file)
			else:
				log.debug('skipping %s, does not have valid extension (.xml or .gz)' % entry)		  
	
	parser.parse()
	
	log('%s total components parsed' % len(parser.parsed_nsanity_components))
	
	# for host in parser.parsed_nsanity_components:
		# print host.fs_list
	# 	for lun in host.lun_list:
	# 		print lun.serial_no, lun.name, lun.model
			
	parser.export()