
from accounts import Account
from commands.account_creator.creator import AccountsCreatorCommand

data = {"accounts":[Account(["ABACO", "Nombre", "puesto", "sucursal", "super_test@etesa.com.mx", "-"])]}
cmd = AccountsCreatorCommand()
cmd.execute(data)

print data["accounts"][0].password

