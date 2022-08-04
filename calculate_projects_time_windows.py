# -*- coding: utf-8 -*-
import os
import sys
import subprocess


def main():
    from pairwise_conflict_dataset.models import Project
    projects = Project.objects.all().order_by('created_at')
    total_count = len(projects)
    for i, project in enumerate(projects):
        print(i + 1, "/", total_count)
        print(project.name)
        # calculate IPE time windows
        print("Calculate IPE time windows")
        subprocess.run(["python", "manage.py", "calculate_ipe_time_windows", "--project_name", project.name, "--time_interval", "14"],
                       capture_output=True)


if __name__ == "__main__":
    # Init Django environment
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pull_request_data_analysis.settings')

    import django
    django.setup()

    main()
