.PHONY: dev build release clean

# 开发模式：启动开发服务器
dev:
	@echo "Stopping existing python -m main processes..."
	@pkill -f "python -m main" || true
	@echo "Starting development server..."
	python -m main

# 构建插件包
build:
	@echo "Building dify plugin package..."
	rm -rf dreamai.difypkg
	rm -rf dreamai.signed.difypkg
	dify plugin package ../dreamai
	dify signature sign  dreamai.difypkg -p ../dreamai.private.pem

# 发布：清理、构建、移动文件并提交到GitHub
release: clean build
	@echo "Creating release directory..."
	mkdir -p release
	@echo "Moving package to release directory..."
	mv ../dreamai.difypkg release/ || echo "Warning: Package file not found"
	@echo "Committing to GitHub..."
	gh release create v$$(date +%Y%m%d-%H%M%S) release/dreamai.difypkg --title "Release $$(date +%Y-%m-%d)" --notes "Automated release"

# 清理release目录
clean:
	@echo "Cleaning release directory..."
	rm -rf release

# 帮助信息
help:
	@echo "Available commands:"
	@echo "  make dev     - Start development server (kills existing processes)"
	@echo "  make build   - Build dify plugin package"
	@echo "  make release - Clean, build, and release to GitHub"
	@echo "  make clean   - Remove release directory"
	@echo "  make help    - Show this help message"