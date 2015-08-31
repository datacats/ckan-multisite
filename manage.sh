#!/bin/bash

ProgName=$(basename $0)
  
sub_help(){
    echo "Usage: $ProgName <subcommand> [options]\n"
    echo "Subcommands:"
    echo "    regenerate   Regenerate the configuration files for nginx"
    echo "    changepw     Changes the password for the ckan-multisite admin."
    echo ""
}
  
sub_regenerate() {
    python -c "from ckan_multisite.router import nginx;nginx.regenerate_config()"
}

sub_changepw() {
    password=""
    password_confirm="n"
    while [ "$password" != "$password_confirm" ]; do
        read -s -p "Please enter the admin user password you wish to use: " password
        echo
        read -s -p "Please confirm the password: " password_confirm
        echo
    done
    pw_hash=$(python -c "from ckan_multisite.pw import encrypt; print encrypt('$password')" | sed -e 's/[\/&]/\\&/g')
    if [ $? != 0 ]; then
        echo 'Python failed. See above output. Could not change pw.'
        exit 1
    fi
    sed -i "s/.*ADMIN_PW.*/ADMIN_PW= '$pw_hash'/gw changes.txt" ckan_multisite/config.py
    if [ -s changes.txt ]; then
        echo 'Password changed successfully.'
        rm changes.txt
    else
        echo 'Pattern not found. Cannot change.'
        rm changes.txt
        exit 1
    fi
}


source ../virtualenv/bin/activate
 
subcommand=$1
case $subcommand in
    "" | "-h" | "--help")
        sub_help
        ;;
    *)
        shift
        sub_${subcommand} $@
        if [ $? = 127 ]; then
            echo "Error: '$subcommand' is not a known subcommand." >&2
            echo "       Run '$ProgName --help' for a list of known subcommands." >&2
            exit 1
        fi
        ;;
esac
