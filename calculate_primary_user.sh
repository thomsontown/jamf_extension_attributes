#!/bin/sh


#	This script was written to determine the primary user of a system. By using a built-in accounting
#	feature we can compare accumulated connection times for each user. The user with the most time
#	logged in and connected to a system is deemed the primary user. To avoid including system accounts
#	only user IDs greater than 500 are evauluated. Additionally, generic user accounts included in a 
#	blacklist are ignored.

#	Author:		Andrew Thomson
#	Date:		10-22-2016


DEFAULT_TIME="0"
DEFAULTS_DOMAIN="com.company"
BLACKLIST=(admin administrator adobeinstall)


#	get array of users
CURRENT_USERS=(`/usr/bin/dscl . list /Users UniqueID | awk '$2 > 500 { print tolower($1) }'`)


#	display error if no valid users found
if [ ${#CURRENT_USERS[@]} -eq 0 ]; then
	echo "ERROR: No users found."
	exit $LINENO
fi


#	enumerate users and compare accumulated connection times
for CURRENT_USER in ${CURRENT_USERS[@]}; do
	
	#	skip if user in blacklist
	if [[ ${BLACKLIST[@]} == *$CURRENT_USER* ]]; then continue; fi
	
	#	get accumulated connection time for user
	CONNECT_TIME=`/usr/sbin/ac $CURRENT_USER | /usr/bin/awk '/total/ {print $2}'`
	
	#	compare connections times
	IS_GREATER=`echo "$CONNECT_TIME > $DEFAULT_TIME" | /usr/bin/bc -l`
	
	#	if current user time is greater than previous user, update default
	if [ "$IS_GREATER" == "1" ]; then
		DEFAULT_USER="$CURRENT_USER"
		DEFAULT_TIME="$CONNECT_TIME"
	fi
done


#	if no default user found exit with error
if [ -z $DEFAULT_USER ]; then
	echo "ERROR: No primary user found."
	exit $LINENO
fi


#	write primary user to disk
/usr/bin/defaults write ${DEFAULTS_DOMAIN%.}.PrimaryUser PrimaryUser -string $DEFAULT_USER 2> /dev/null
/usr/bin/defaults write ${DEFAULTS_DOMAIN%.}.PrimaryUser LastUpdateCheck -date "`date +"%Y-%m-%d %l:%M:%S +0000"`" 2> /dev/null


#	output result tag for extension attribute
echo "<result>$DEFAULT_USER</result>"