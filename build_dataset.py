# -*- coding: utf-8 -*-
import os
import sys
import time
import subprocess


def main():
    from pairwise_conflict_dataset.models import Project
    projects = Project.objects.filter(pairwise_conflicts_count__isnull=True).order_by('created_at')
    total_count = len(projects)
    for i, project in enumerate(projects):
        project.pairwise_conflicts_count = 0
        project.save()
        print(i + 1, "/", total_count)
        print(project.name)
        # import commits
        print("Import commits")
        subprocess.run(["python", "manage.py", "import_commits", "--project_name", project.name],
                       capture_output=True)
        # import pull requests
        print("Import pull requests")
        subprocess.run(["python", "manage.py", "import_pull_requests", "--project_name", project.name],
                       capture_output=True)
        # upgrade pull requests info
        prs_count = project.pull_requests.filter(merged=True,
                                                 github_raw_data__isnull=True).count()
        times = int(prs_count / 5000) + 1
        for t in range(times):
            print("Upgrade PRs info:", t + 1, "/", times)
            subprocess.run(["python", "manage.py", "upgrade_pull_request_info", "--project_name", project.name],
                           capture_output=True)
            if t < times - 1:
                time.sleep(15 * 60)  # 15 minutes
        # get pairwise conflicts
        print("get pairwise conflicts")
        subprocess.run(["python", "manage.py", "get_pairwise_conflicts", "--project_name", project.name],
                       capture_output=True)
        project.get_pairwise_conflicts_count(recalculate=True)
        project.get_data_quality_percentage(recalculate=True)


if __name__ == "__main__":
    # Init Django environment
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    sys.path.insert(0, parent_dir)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pull_request_data_analysis.settings')

    import django
    django.setup()

    main()
