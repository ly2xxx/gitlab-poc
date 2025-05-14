#!/usr/bin/env python3
import yaml
import os
import sys
from collections import defaultdict
#sample call - python parse_gitlab_ci.py templates/java-pipeline.yml

def parse_gitlab_ci(file_path):
    """Parse GitLab CI YAML file and analyze stages and dependencies."""
    try:
        # Open file with 'utf-8' encoding and ignore character errors
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            ci_config = yaml.safe_load(file)
    except Exception as e:
        print(f"Error reading or parsing YAML file: {e}")
        return None
    
    # Extract includes
    includes = ci_config.get('include', [])
    included_files = {}
    for include in includes:
        if 'file' in include and 'project' in include:
            included_files[include['file']] = include['project']
    
    # Extract stages
    stages = ci_config.get('stages', [])
    
    # Map jobs to stages and their extensions
    jobs_by_stage = defaultdict(list)
    job_extensions = {}
    
    for job_name, job_config in ci_config.items():
        if isinstance(job_config, dict) and 'stage' in job_config:
            stage = job_config['stage']
            jobs_by_stage[stage].append(job_name)
            
            # Check if job extends another job
            if 'extends' in job_config:
                job_extensions[job_name] = job_config['extends']
    
    return {
        'included_files': included_files,
        'stages': stages,
        'jobs_by_stage': jobs_by_stage,
        'job_extensions': job_extensions
    }

def map_jobs_to_included_files(parsed_data):
    """Map jobs to their included files based on extensions."""
    result = {}
    
    # Simple mapping for now - this would need enhancement to actually parse the included files
    for stage, jobs in parsed_data['jobs_by_stage'].items():
        result[stage] = []
        for job in jobs:
            if job in parsed_data['job_extensions']:
                extension = parsed_data['job_extensions'][job]
                # Assuming extension name (without dot) corresponds to part of the included file name
                if isinstance(extension, str) and extension.startswith('.'):
                    extension_name = extension[1:]  # Remove the dot
                    for file_path in parsed_data['included_files'].keys():
                        if extension_name in file_path:
                            result[stage].append({
                                'job': job,
                                'extends': extension,
                                'included_file': file_path,
                                'project': parsed_data['included_files'][file_path]
                            })
                            break
    
    return result

def main():
    if len(sys.argv) < 2:
        print("Usage: python parse_gitlab_ci.py <path_to_gitlab_ci_yaml>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        sys.exit(1)
    
    parsed_data = parse_gitlab_ci(file_path)
    if not parsed_data:
        sys.exit(1)
    
    print(f"\nAnalyzing GitLab CI file: {file_path}\n")
    
    print("Included files:")
    for file_path, project in parsed_data['included_files'].items():
        print(f"  - {file_path} (from project: {project})")
    
    print("\nStages defined in pipeline:")
    for stage in parsed_data['stages'] or sorted(parsed_data['jobs_by_stage'].keys()):
        print(f"  - {stage}")
    
    print("\nJobs by stage:")
    for stage, jobs in parsed_data['jobs_by_stage'].items():
        print(f"  Stage: {stage}")
        for job in jobs:
            extension = parsed_data['job_extensions'].get(job, "None")
            print(f"    - {job} (extends: {extension})")
    
    print("\nMapping jobs to included files:")
    job_mapping = map_jobs_to_included_files(parsed_data)
    for stage, mappings in job_mapping.items():
        print(f"  Stage: {stage}")
        for mapping in mappings:
            print(f"    - Job: {mapping['job']}")
            print(f"      Extends: {mapping['extends']}")
            print(f"      Included file: {mapping['included_file']}")
            print(f"      Project: {mapping['project']}")
            print()

if __name__ == "__main__":
    main()