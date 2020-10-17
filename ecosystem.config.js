module.exports = {
  apps : [{
    name: 'NPC',
    script: 'main.py',
    watch: '.',
    interpreter: '/usr/bin/python3.8',
    args: '/home/ubuntu/Documents/NP_C/ids/noporn.json'
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
