"""
Bulk Repository Cloner
Clones popular open-source repositories for indexing
"""

import os
import subprocess
from pathlib import Path
import time

# Popular repositories across different languages and domains
POPULAR_REPOS = [
    # Python - Web Frameworks
    "https://github.com/django/django",
    "https://github.com/pallets/flask",
    "https://github.com/encode/django-rest-framework",
    "https://github.com/tiangolo/fastapi",
    "https://github.com/pallets/click",
    
    # Python - Data Science & ML
    "https://github.com/scikit-learn/scikit-learn",
    "https://github.com/pandas-dev/pandas",
    "https://github.com/numpy/numpy",
    "https://github.com/matplotlib/matplotlib",
    "https://github.com/scipy/scipy",
    "https://github.com/keras-team/keras",
    "https://github.com/pytorch/pytorch",
    "https://github.com/tensorflow/tensorflow",
    
    # Python - Utilities
    "https://github.com/psf/requests",
    "https://github.com/python/cpython",
    "https://github.com/ansible/ansible",
    "https://github.com/scrapy/scrapy",
    "https://github.com/certbot/certbot",
    
    # JavaScript - Frontend Frameworks
    "https://github.com/facebook/react",
    "https://github.com/vuejs/vue",
    "https://github.com/angular/angular",
    "https://github.com/sveltejs/svelte",
    "https://github.com/jquery/jquery",
    
    # JavaScript - Backend & Tools
    "https://github.com/nodejs/node",
    "https://github.com/expressjs/express",
    "https://github.com/nestjs/nest",
    "https://github.com/meteor/meteor",
    "https://github.com/vercel/next.js",
    
    # JavaScript - Build Tools
    "https://github.com/webpack/webpack",
    "https://github.com/vitejs/vite",
    "https://github.com/parcel-bundler/parcel",
    "https://github.com/babel/babel",
    
    # TypeScript
    "https://github.com/microsoft/TypeScript",
    "https://github.com/denoland/deno",
    
    # Java - Frameworks
    "https://github.com/spring-projects/spring-boot",
    "https://github.com/spring-projects/spring-framework",
    "https://github.com/elastic/elasticsearch",
    "https://github.com/apache/kafka",
    "https://github.com/apache/spark",
    
    # Go
    "https://github.com/golang/go",
    "https://github.com/kubernetes/kubernetes",
    "https://github.com/moby/moby",
    "https://github.com/prometheus/prometheus",
    "https://github.com/gin-gonic/gin",
    "https://github.com/gofiber/fiber",
    
    # Rust
    "https://github.com/rust-lang/rust",
    "https://github.com/tokio-rs/tokio",
    "https://github.com/actix/actix-web",
    
    # C/C++
    "https://github.com/torvalds/linux",
    "https://github.com/microsoft/terminal",
    "https://github.com/redis/redis",
    "https://github.com/postgres/postgres",
    "https://github.com/nginx/nginx",
    "https://github.com/opencv/opencv",
    "https://github.com/grpc/grpc",
    
    # Ruby
    "https://github.com/rails/rails",
    "https://github.com/jekyll/jekyll",
    "https://github.com/discourse/discourse",
    
    # PHP
    "https://github.com/laravel/laravel",
    "https://github.com/symfony/symfony",
    "https://github.com/WordPress/WordPress",
    
    # DevOps & Tools
    "https://github.com/docker/docker-ce",
    "https://github.com/hashicorp/terraform",
    "https://github.com/ansible/ansible",
    "https://github.com/grafana/grafana",
    
    # Editors & IDEs
    "https://github.com/microsoft/vscode",
    "https://github.com/atom/atom",
    "https://github.com/neovim/neovim",
    
    # Databases
    "https://github.com/mongodb/mongo",
    "https://github.com/cockroachdb/cockroach",
    "https://github.com/etcd-io/etcd",
    
    # Mobile
    "https://github.com/flutter/flutter",
    "https://github.com/ionic-team/ionic-framework",
    "https://github.com/react-native-community/react-native-maps",
    
    # Games & Graphics
    "https://github.com/godotengine/godot",
    "https://github.com/mrdoob/three.js",
    
    # Security
    "https://github.com/OWASP/owasp-mstg",
    "https://github.com/sqlmapproject/sqlmap",
    
    # Cloud Native
    "https://github.com/istio/istio",
    "https://github.com/helm/helm",
    "https://github.com/containerd/containerd",
]

def clone_repository(repo_url: str, base_dir: Path, depth: int = 1) -> bool:
    """Clone a single repository"""
    repo_name = repo_url.split('/')[-1].replace('.git', '')
    repo_path = base_dir / repo_name
    
    # Skip if already exists
    if repo_path.exists():
        print(f"⏭️  Skipping {repo_name} (already exists)")
        return True
    
    print(f"📥 Cloning {repo_name}...")
    
    try:
        # Use --depth 1 for shallow clone to save space and time
        cmd = f'git clone --depth {depth} {repo_url} "{repo_path}"'
        
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            print(f"✅ Cloned {repo_name}")
            return True
        else:
            print(f"❌ Failed to clone {repo_name}: {result.stderr[:100]}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏱️  Timeout cloning {repo_name} (skipping)")
        return False
    except Exception as e:
        print(f"❌ Error cloning {repo_name}: {str(e)[:100]}")
        return False

def clone_all_repos(repos: list, base_dir: str = "./cloned_repos", max_repos: int = None):
    """Clone all repositories in the list"""
    base_path = Path(base_dir)
    base_path.mkdir(exist_ok=True)
    
    if max_repos:
        repos = repos[:max_repos]
    
    print("=" * 60)
    print(f"🚀 BULK REPOSITORY CLONER")
    print("=" * 60)
    print(f"Target directory: {base_path.absolute()}")
    print(f"Repositories to clone: {len(repos)}")
    print(f"Starting at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    successful = 0
    failed = 0
    skipped = 0
    
    start_time = time.time()
    
    for i, repo_url in enumerate(repos, 1):
        print(f"\n[{i}/{len(repos)}] ", end="")
        
        result = clone_repository(repo_url, base_path)
        
        if result:
            if (base_path / repo_url.split('/')[-1].replace('.git', '')).exists():
                if any((base_path / repo_url.split('/')[-1].replace('.git', '')).iterdir()):
                    successful += 1
                else:
                    skipped += 1
            else:
                skipped += 1
        else:
            failed += 1
        
        # Progress update every 10 repos
        if i % 10 == 0:
            elapsed = time.time() - start_time
            avg_time = elapsed / i
            remaining = (len(repos) - i) * avg_time
            print(f"\n📊 Progress: {i}/{len(repos)} | Success: {successful} | Failed: {failed} | Est. remaining: {remaining/60:.1f}min")
    
    total_time = time.time() - start_time
    
    print("\n" + "=" * 60)
    print("📊 CLONING SUMMARY")
    print("=" * 60)
    print(f"✅ Successfully cloned: {successful}")
    print(f"⏭️  Skipped (already exist): {skipped}")
    print(f"❌ Failed: {failed}")
    print(f"⏱️  Total time: {total_time/60:.2f} minutes")
    print(f"📁 Repositories in: {base_path.absolute()}")
    print("=" * 60)
    
    return successful

def estimate_repo_sizes():
    """Show estimated sizes and counts"""
    print("\n📊 REPOSITORY STATISTICS")
    print("=" * 60)
    print(f"Total repositories available: {len(POPULAR_REPOS)}")
    print("\nBreakdown by category:")
    print(f"  Python: ~20 repos")
    print(f"  JavaScript/TypeScript: ~15 repos")
    print(f"  Java: ~5 repos")
    print(f"  Go: ~6 repos")
    print(f"  C/C++: ~8 repos")
    print(f"  Others: ~30+ repos")
    print("\nEstimated total lines of code: 50M+ lines")
    print("Estimated disk space: 5-10 GB")
    print("Estimated clone time: 30-60 minutes")
    print("=" * 60)

def main():
    """Main function"""
    print("\n🔍 AI-Powered Code Search - Repository Cloner")
    
    estimate_repo_sizes()
    
    print("\nOptions:")
    print("1. Clone ALL repositories (~90 repos, 50M+ lines)")
    print("2. Clone FIRST 20 repositories (~10M lines, faster)")
    print("3. Clone FIRST 50 repositories (~25M lines)")
    print("4. Custom number")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    max_repos = None
    if choice == "2":
        max_repos = 20
    elif choice == "3":
        max_repos = 50
    elif choice == "4":
        num = input("How many repos to clone? ").strip()
        if num.isdigit():
            max_repos = int(num)
    
    confirm = input(f"\n⚠️  This will clone {max_repos if max_repos else len(POPULAR_REPOS)} repositories. Continue? (yes/no): ").strip().lower()
    
    if confirm == "yes":
        clone_all_repos(POPULAR_REPOS, max_repos=max_repos)
        
        print("\n✅ Cloning complete!")
        print("\n🔍 Next steps:")
        print("1. Run: python code_search_engine.py")
        print("2. Choose option 1 (Index local directory)")
        print("3. Enter path: cloned_repos")
        print("4. Wait for indexing to complete")
        print("\nThis will give you 50M+ lines indexed!")
    else:
        print("❌ Cancelled")

if __name__ == "__main__":
    main()