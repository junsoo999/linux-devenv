#!/bin/bash

##########################################################################
##  Install Directory Structure
##
##  Authors:  Junsoo    Kim   ( js.kim@hyperaccel.ai        )
##  Version:  0.0.1
##  Date:     2025-07-05      ( v0.0.1, init                )
##
##########################################################################

# Create top directories
mkdir -p $HOME/documents
mkdir -p $HOME/downloads
mkdir -p $HOME/projects
mkdir -p $HOME/tasks

# Create projects directory
mkdir -p $HOME/projects/aida
mkdir -p $HOME/projects/bertha

# Create setup.sh files for project directories with useful aliases
cat > $HOME/projects/aida/.setup.sh << 'EOF'
#!/bin/zsh

# AIDA Project
alias aida='cd $AIDA_HOME'
EOF

cat > $HOME/projects/bertha/.setup.sh << 'EOF'
#!/bin/zsh

# BERTHA Project
alias ber='cd $BERTHA_HOME'
EOF

##########################################################################
