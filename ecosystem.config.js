module.exports = {
  apps : [{
    name: 'NPC',
    script: 'main.py',
    watch: ['main.py','streak.py','utils.py'],
    interpreter: '/usr/bin/python3.8',
    args: '/home/ubuntu/Documents/NP_C/ids/noporn.json mysql+pymysql://bot:Genesis_Affair1998@192.168.1.180/np_db'
  }],

  deploy : {
    production : {
      user : 'SSH_USERNAME',
      host : 'SSH_HOSTMACHINE',
      ref  : 'origin/master',
      repo : 'GIT_REPOSITORY',
      path : 'DESTINATION_PATH',
      'pre-deploy-local': '',
      'post-deploy' : 'npm install && pm2 reload ecosystem.config.js --env production',
      'pre-setup': ''
    }
  }
};
