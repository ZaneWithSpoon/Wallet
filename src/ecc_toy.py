#!/usr/bin/env python
""" wallet.py
    
    Copyrigth 2017, Paul A. Lambert
"""
from ecc.curves import SECP_256k1
import os
import pwd
import click
import pyqrcode


DEFAULT_CIPHERSUITE = 'Bitcoin'
cipher_suite_name_list = ('Sweetpea', 'ChaCha_Poly', 'SuiteB', 'Bitcoin', 'Ethereum')

def default_wallet_path():
    user_dir = pwd.getpwuid(os.geteuid()).pw_dir
    return user_dir + '/.tip/wallet'

class Wallet:
    """
    """

    def default_wallet_path():
        user_dir = pwd.getpwuid(os.geteuid()).pw_dir
        return user_dir + '/.tip/wallet'

    @classmethod
    def open_wallet_file(cls, wallet_path):
        """ Open a wallet from a file. """
        if not wallet_path:
            wallet_path = default_wallet_path()
        with click.open_file( wallet_path, 'r' ) as f:
            wallet_text = f.read()
        print wallet_text
        wallet = Wallet()
        # create personas from the wallet_text descriptions
        wallet.persona_list = []
        for persona_struct in yaml.safe_load_all( wallet_text ):
            pd = Persona_Data(persona_struct) # a map with a single Persona
            wallet.persona_list.append( pd.value['persona'] )
        return wallet

    def newPersona(self, local_name=None, cipher_suite_name=DEFAULT_CIPHERSUITE):
        """ Create a new persona in the wallet. """
        persona = Persona.new( cipher_suite_name, local_name )
        if not local_name:
            # create a unique identifier / name
            # use text string representation of uaid
            raise "unique name code tbd"
        return persona

    def write_wallet_file(self, wallet_path):
        """ Write wallet structure to file. """

        persona_data_struct_list = []
        for persona in self.persona_list:
            persona_data_struct_list.append( {'persona': persona.toStruct()} )

        if not wallet_path:
            wallet_path = default_wallet_path()

        wallet_txt = yaml.dump_all(persona_data_struct_list, default_flow_style=False, explicit_start=True)
        with click.open_file(wallet_path, 'w') as f:
            f.write( wallet_txt )


# ---- Command line interface -----------------------------
class Options(object):
    def __init__(self):
        self.verbose = False
pass_options = click.make_pass_decorator(Options, ensure=True)

@click.group(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('--cipher_suite', '-c', 'cipher_suite_name',
              type=click.Choice( cipher_suite_name_list ),
              default=DEFAULT_CIPHERSUITE,
              help="Cipher suite to use for the command.")
@click.option('--verbose', '-v', is_flag=True, default=False,
              help='Verbose output')
@click.option('--wallet', '-w', 'wallet_path', type=click.Path(exists=True),
               default=None,
               help="Path to wallet, default is ~/.tip/wallet")
@pass_options
def cli(options, cipher_suite_name, verbose, wallet_path): # entry point for cli
    """ A Wallet to manage cryptographic Personas.
    """
    options.cipher_suite_name = cipher_suite_name
    options.verbose = verbose
    # if path not specified, open ~/.tip/wallet
    if not wallet_path:
        user_dir = pwd.getpwuid(os.geteuid()).pw_dir
        wallet_path = user_dir + '/.tip/wallet'
    options.wallet_path = wallet_path

# QR code output of Persona
# ---- tip [options] qr [-p][-t][--qz NUM] -----------------------------
@cli.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('--txt', '-t', 'out_format', flag_value='txt', default=True,
              help='Output a text version of the QR code.')
@click.option('--png', '-p', 'out_format', flag_value='png',
              help='Output a png image of the QR code.')
@click.option('--qz', 'quiet_zone', default=1,
              help='Set size of quiet zone around QR code.')
@pass_options
def qr(options, out_format, quiet_zone):
    """ Output as QR code.
    """
    wallet=Wallet(options.wallet_path)

    qr_string = 't:' + '123123123'
    qr = pyqrcode.create( qr_string )
    text_qr = qr.terminal(quiet_zone=quiet_zone)
    click.echo(text_qr)

# ---- tip [options] list ----------------------------------------------
@cli.command()
@pass_options
def list(options):
    """ List available Personas in a wallet. """

    wallet = Wallet.open_wallet_file( options.wallet_path )

    for persona in wallet.persona_list:
        if options.verbose:
            click.echo( str(persona) )
        else:
            click.echo("{:10s} {:10s} {}".format(
                        persona.value['local name'].value,
                        persona.value['key pair'].value['csi'],
                        persona.value['key pair'].value['uaid']) )

# ---- tip [options] new [-p <name] ------------------------------------
@cli.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('--name', '-n', 'persona_name', default=None,
              help='The local name of the persona.')
@pass_options
def new(options, persona_name):
    """ Create a new Persona. """
    wallet = Wallet.open_wallet_file( options.wallet_path )
    for p in wallet.persona_list:
        if persona_name == p.value['local name'].value:
            raise ValueError( "Persona name already exists in wallet" )

    p = Persona.new( options.cipher_suite_name, persona_name )
    wallet.persona_list.append( p )
    # serialize and write wallet with new persona last
    wallet.write_wallet_file( options.wallet_path )

@cli.command(context_settings=dict(help_option_names=['-h', '--help']))
@pass_options
def dump(options):
    """ Readable dump of wallet. """
    wallet = Wallet.open_wallet_file( options.wallet_path )
    click.echo('dump ...')


if __name__ == '__main__':
    cli()
