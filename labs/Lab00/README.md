# Lab 00 — Docker + testing basics (orientation)

## Learning goals

- Install Docker Desktop or Docker Engine and verify it runs.
- Understand images vs containers and how tags/registries work.
- Use volumes and networks to persist data and connect services.
- Build a Dockerfile and run a multi-service app with Compose.
- Run pytest and interpret test output.

## In-class walkthrough

1. **Install + verify Docker**
   - Start Docker (in Windows start Docker Desktop)
   - Check `docker version` and `docker info`.
   - Checl `docker compose version` (will be needed later)
   - Run `docker run --rm hello-world`.

   - Try busybox:
   `docker run busybox`

   - Now try `docker run -it busybox bash`
   - run `echo "Hello from container" > new_file.txt`
   - exec a command within a container: `docker exec busybox echo "hi from the container interactive terminal"`
   - exec a command within a container: `docker exec busybox cat new_file.txt`

   - See running containers from host `docker ps`
   - Now exit the container and run it again `docker run -it busybox` Where's the new_file.txt ???
     Each time we run a container it starts fresh. If no volumes are created nothing persists

     **by default every time you run a container it starts fresh**, and nothing you change inside it will persist once it stops or is removed, *unless you explicitly add persistence*.

      Here’s how it works:

      ---

      #### 🧠 Default Behavior

      When you do:

      ```bash
      docker run busybox sh
      ```

      …you get a **fresh container from the image**.

      Any changes you make (files created, config edited, packages installed) exist **only in that container instance’s writable layer**.

      If the container is stopped and removed:

      ```bash
      docker stop my-container
      docker rm my-container
      ```

      **ALL changes are lost**.

      ---

      #### 💾 Persistence Only Happens With:

      ##### 📌 1. **Volumes**

      A Docker volume stores data outside the container’s writable layer.

      Example:

      ```bash
      docker run -v mydata:/data busybox sh -c "echo hello > /data/file.txt"
      ```

      The file persists in the `mydata` volume even if the container is removed.

      ---

      ##### 📌 2. **Bind Mounts**

      You mount a directory from the host:

      ```bash
      docker run -v ./my-data:/data busybox sh -c "echo hello > /data/file.txt"
      ```
      edit the file and verify
      ```bash
      docker run -v ./my-data:/data busybox sh -c "cat /data/file.txt"
      ```

      The file stays on the host file system.

      ---

      ##### 📌 3. **Committing to a New Image**

      You can “snapshot” a container’s state:

      ```bash
      docker commit my-container myimage
      ```

      Then run new containers from `myimage` with those changes baked in.

      ---

      #### 📍 Summary

      | Scenario                       | Does Data Persist? |
      | ------------------------------ | ------------------ |
      | Container stopped & removed    | ❌ No               |
      | Data in container’s filesystem | ❌ Lost at removal  |
      | Volume or bind mount           | ✅ Yes              |
      | Committed to new image         | ✅ Yes              |

      ---




2. **Images vs containers**

   - `docker pull python:3.12-slim` and `docker images`.
   - Start a container with `docker run --rm -it python:3.12-slim bash`.

3. **Volumes + networking**

   - Bind mount a local folder: `docker run --rm -v $(pwd):/work -w /work python:3.12-slim ls`.
   - Create a user-defined network and attach two containers.

4. **Build + Compose**

   - Write a simple `Dockerfile` for a tiny Python app.
   - Write a `compose.yaml` that builds the image and runs two services.
   - Demonstrate `docker compose up --build` and `docker compose down -v`.

5. **Pytest basics**

   - Run `pytest -q` and interpret the pass/fail summary.
   - Show how to inspect a failing assertion and use `-x` or `-k`.

```sh {"interactive":"false"}
docker version
```

```sh
docker info
```

## Student deliverable

- A small repo containing:
   - `Dockerfile` and `compose.yaml` that run a tiny web or CLI service.
   - A `tests/` folder with at least one pytest test.
   - A short `README.md` with instructions for running locally and via Docker.

## Instructor notes

- Emphasize reproducibility: same image, same result for grading.
- Demonstrate a common failure (missing dependency) and show how Docker fixes it.
- Explain how volumes map to host filesystem and why `-v` is useful for labs.
- Encourage students to read Compose logs and to `docker compose ps`.

## Tools (free + open source)

- Docker Engine / Docker Desktop (community).
- Docker Compose v2.
- Python 3.11+.
- pytest.

## Suggested reading & sources

- Docker overview: https://docs.docker.com/get-started/overview/
- Dockerfile reference: https://docs.docker.com/engine/reference/builder/
- Compose file specification: https://docs.docker.com/compose/compose-file/
- pytest intro: https://docs.pytest.org/en/stable/getting-started.html
