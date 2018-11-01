package main

import (
	"context"

	"encoding/json"

	"fmt"

	"io"

	"log"

	"os"

	"strconv"

	"github.com/docker/docker/api/types"
	"github.com/docker/go-connections/nat"

	"github.com/docker/docker/api/types/container"

	"github.com/docker/docker/client"
)

type ContainerType struct {
	ConName string `json:"conName"`

	ImageName string `json:"imageName"`

	Port int `json:"port"`

	ID string `json:"id"`
}

func (c *ContainerType) RunContainer() {

	ctx := context.Background()

	cli, err := client.NewClientWithOpts(client.WithVersion("1.37"))

	if err != nil {

		panic(err)

	}

	out, err := cli.ImagePull(ctx, c.ImageName, types.ImagePullOptions{})

	if err != nil {

		panic(err)

	}

	io.Copy(os.Stdout, out)

	portString := strconv.Itoa(c.Port) + "/tcp"

	config := &container.Config{

		Image: c.ImageName,
		ExposedPorts: nat.PortSet{
			nat.Port(portString): {},
		},
	}

	resp, err := cli.ContainerCreate(ctx, config, nil, nil, c.ConName)

	if err != nil {

		panic(err)

	}

	c.ID = resp.ID

	if err := cli.ContainerStart(ctx, resp.ID, types.ContainerStartOptions{}); err != nil {

		panic(err)

	}

	log.Println(resp.ID)

}

func (c *ContainerType) DestroyContainer() error {

	return nil

}

func printContainer(container types.Container) {

	res2B, _ := json.MarshalIndent(container, "", "\t")

	fmt.Println(string(res2B))

}

func listContainer() {

	cli, err := client.NewEnvClient()

	if err != nil {

		panic(err)

	}

	containers, err := cli.ContainerList(context.Background(), types.ContainerListOptions{})

	if err != nil {

		panic(err)

	}

	for _, container := range containers {

		fmt.Println(container.ID)

		fmt.Println(container.Names[0])

	}

}

func getContainer(container_name string) types.Container {

	cli, err := client.NewEnvClient()

	if err != nil {

		panic(err)

	}

	//containers, err := cli.ContainerList

	//containers, err := cli.ContainerList(context.Background(), types.ContainerListOptions.Filters  ({"name": [container_name]}))

	containers, err := cli.ContainerList(context.Background(), types.ContainerListOptions{})

	//io.Copy(os.Stdout, containers)

	if err != nil {

		panic(err)

	}

	var containerTodel types.Container

	for _, container := range containers {

		if container.Names[0] == container_name {

			containerTodel = container

		}

		//fmt.Println(container.name)

	}

	printContainer(containerTodel)

	return containerTodel

}

func (c *ContainerType) stopContainer(conainerName string) {

	conterToDel := getContainer(conainerName)

	ctx := context.Background()

	cli, err := client.NewEnvClient()

	if err != nil {

		panic(err)

	}

	/*containers, err := cli.ContainerList(ctx, types.ContainerListOptions{})

	  if err != nil {

	      panic(err)

	  }*/

	//for _, container := range conterToDel {

	//container = types.Container(container)

	fmt.Print("Stopping container ", conterToDel.ID, "... ")

	if err := cli.ContainerStop(ctx, conterToDel.ID, nil); err != nil {

		panic(err)

	}

	fmt.Println("Success")

	//}

}

func printContainerLog(containerId string) {

	ctx := context.Background()

	cli, err := client.NewEnvClient()

	if err != nil {

		panic(err)

	}

	options := types.ContainerLogsOptions{ShowStdout: true}

	// Replace this ID with a container that really exists

	out, err := cli.ContainerLogs(ctx, containerId, options)

	if err != nil {

		panic(err)

	}

	io.Copy(os.Stdout, out)

}

func ListAllImage() {

	cli, err := client.NewEnvClient()

	if err != nil {

		panic(err)

	}

	images, err := cli.ImageList(context.Background(), types.ImageListOptions{})

	if err != nil {

		panic(err)

	}

	for _, image := range images {

		//res, _ := json.MarshalIndent(image, "", "\t")

		//fmt.Println(string(res))

		fmt.Println(image.ID)

	}

}

func pullImage(imageName string) {

	ctx := context.Background()

	cli, err := client.NewEnvClient()

	if err != nil {

		panic(err)

	}

	out, err := cli.ImagePull(ctx, imageName, types.ImagePullOptions{})

	if err != nil {

		panic(err)

	}

	defer out.Close()

	io.Copy(os.Stdout, out)

}
